import logging
import pprint

import requests
from werkzeug import urls

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class RevolutController(http.Controller):
    @http.route(["/payment/revolut/return"], type="http", auth="public", csrf=False)
    def revolut_form_feedback(self, **post):
        """
        Handles the return callback from Revolut after payment processing.
        Validates the payment reference, retrieves payment details via API,
        and triggers the notification handler on the transaction.
        """
        _logger.info("Revolut return post data: %s", pprint.pformat(post))

        reference = post.get("reference")
        if not reference:
            _logger.error("Missing reference in return data.")
            return request.redirect("/payment/status")

        # Get Revolut payment provider
        provider = (
            request.env["payment.provider"]
            .sudo()
            .search([("code", "=", "revolut")], limit=1)
        )
        if not provider:
            _logger.error("Revolut provider not found.")
            return request.redirect("/payment/status")

        # Search for payment transaction using reference and provider
        transaction = (
            request.env["payment.transaction"]
            .sudo()
            .search(
                [
                    ("reference", "=", reference),
                    ("provider_id", "=", provider.id),
                ],
                limit=1,
            )
        )
        if not transaction:
            _logger.error("Transaction not found for reference: %s", reference)
            return request.redirect("/payment/status")

        # Fetch payment details from Revolut
        payment_details = self._fetch_revolut_payment_details(
            provider, transaction.provider_reference
        )
        if not payment_details:
            _logger.error(
                "Failed to retrieve payment details from Revolut " "for reference: %s",
                reference,
            )
            return request.redirect("/payment/status")

        # Pass data to the notification handler to update payment status
        payment_details.update({"description": reference})
        transaction._handle_notification_data("revolut", payment_details)

        return request.redirect("/payment/status")

    def _fetch_revolut_payment_details(self, provider, payment_id):
        """
        Fetches payment details from Revolut using the order/payment ID.

        :param provider: payment.provider record for Revolut
        :param payment_id: ID from provider (usually order ID)
        :return: dict with payment details if successful, else None
        """
        try:
            revolut_url = urls.url_join(
                provider.get_revolut_base_url(),
                f"api/orders/{payment_id}",
            )
            headers = {
                "Accept": "application/json",
                "Revolut-Api-Version": "2023-09-01",
                "Authorization": (f"Bearer {provider.revolut_authentication_key}"),
            }
            response = requests.get(revolut_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            _logger.error("Revolut API request timed out.")
            raise ValidationError(
                _(
                    "Revolut: Payment service is currently unresponsive, "
                    "please try again later."
                )
            ) from None
        except requests.exceptions.RequestException as e:
            _logger.error("Revolut API error: %s", e)
            return None
