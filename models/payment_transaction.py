import json
import logging

import requests
from odoo.http import request
from werkzeug import urls

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        """
        Generate Revolut-specific rendering values for the transaction.
        This method is triggered during payment form rendering.
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "revolut":
            return res

        # Prepare Revolut API endpoint and payload
        revolut_url = urls.url_join(
            self.provider_id.get_revolut_base_url(), "api/orders"
        )
        if processing_values['provider_code'] == 'revolut':
            _logger.info("processing_values['provider_code] value: %s", processing_values['provider_code'])
            _logger.info("self.invoice_ids[0].journal_id.currency_id.name: %s", self.invoice_ids[0].journal_id.currency_id.name)
            currency = self.invoice_ids[0].journal_id.currency_id.name
        else:
            currency = processing_values.get("currency", self.currency_id.name)
        payload = json.dumps(
            {
                "amount": int(processing_values.get("amount") * 100),
                "currency": currency,
                "description": processing_values.get("reference"),
                "redirect_url": urls.url_join(
                    request.httprequest.url_root,
                    (
                        f"payment/revolut/return?"
                        f"reference={processing_values.get('reference')}"
                    ),
                ),
            }
        )
        _logger.info("payload: %s",payload)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Revolut-Api-Version": "2023-09-01",
            "Authorization": (f"Bearer {self.provider_id.revolut_authentication_key}"),
        }

        try:
            response = requests.post(
                revolut_url, headers=headers, data=payload, timeout=10
            )
            _logger.info("Revolut API response: %s", response.content)
            if response.status_code != 201:
                _logger.error(
                    "Revolut API error %s: %s",
                    response.status_code,
                    response.text,
                )
                raise ValidationError(_("Revolut: Failed to generate payment link."))
            data = response.json()
            _logger.info("Revolut API response: %s", data)

            # Save provider reference from response
            self.provider_reference = data.get("id")

            return {
                "api_url": data.get("checkout_url"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "description": data.get("description"),
            }

        except requests.exceptions.Timeout:
            _logger.error("Revolut API request timed out.")
            raise ValidationError(
                _(
                    "Revolut: Payment service is currently unresponsive, "
                    "please try again later."
                )
            ) from None

        except requests.exceptions.RequestException as e:
            _logger.error("Revolut API request failed: %s", e)
            raise ValidationError(
                _("Revolut: Failed to process payment: %s") % e
            ) from e

    @api.model
    def _get_tx_from_notification_data(self, code, data):
        """
        Find and return the transaction based on
        incoming notification data from Revolut.
        """
        tx = super()._get_tx_from_notification_data(code, data)
        if code != "revolut":
            return tx

        description = data.get("description")
        if not description or not isinstance(description, str):
            raise ValidationError(
                _("Revolut: Invalid or missing 'description' in feedback data.")
            )

        tx = self.search(
            [
                ("provider_reference", "=", data.get("id")),
                ("provider_code", "=", "revolut"),
            ]
        )
        if not tx:
            # Fallback: extract reference from description
            reference = description.split("-")[0].strip()
            tx = self.search(
                [
                    ("reference", "=", reference),
                    ("provider_code", "=", "revolut"),
                ]
            )
            if not tx:
                raise ValidationError(
                    _("Revolut: No transaction found matching reference '%s'.")
                    % reference
                )
        return tx

    def _process_notification_data(self, data):
        """
        Process Revolut payment status notification and update the transaction.
        """
        super()._process_notification_data(data)
        if self.provider_code != "revolut":
            return
        return self._revolut_s2s_validate_tree(data)

    def _revolut_s2s_validate_tree(self, response):
        """
        Handle validation and update from Revolut server-to-server response.
        """
        self.ensure_one()

        state = response.get("state")
        payment_id = response.get("id")
        failure_reason = response.get("failure_reason", "")

        # Update provider reference if not already set
        if payment_id and payment_id != self.provider_reference:
            self.provider_reference = payment_id

        # Map Revolut states to Odoo states
        if state in ["completed", "succeeded"]:
            self.sudo().write(
                {
                    "state_message": "Payment has been successfully completed.",
                }
            )
            self._set_done()
            return True

        elif state == "pending":
            self.sudo().write(
                {
                    "state_message": (
                        "Payment is processing. Payment will reflect within "
                        "3 business days."
                    ),
                }
            )
            self._set_pending()
            return True

        elif state == "failed":
            error_msg = failure_reason or "Payment failed"
            _logger.warning(error_msg)
            self.sudo().write({"state_message": error_msg})
            self._set_error(error_msg)
            return False

        elif state in ["declined", "rejected"]:
            error_msg = failure_reason or f"Payment {state}"
            _logger.warning(error_msg)
            self.sudo().write({"state_message": error_msg})
            self._set_canceled()
            return False

        else:
            error_msg = f"Unknown payment state: {state}"
            _logger.warning(error_msg)
            self.sudo().write({"state_message": error_msg})
            self._set_error(error_msg)
            return False
