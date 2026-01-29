import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentAcquirerRevolut(models.Model):
    _inherit = "payment.provider"

    # Extend provider selection to include Revolut
    code = fields.Selection(
        selection_add=[("revolut", "Revolut Payments")],
        ondelete={"revolut": "set default"},
    )

    # Field to store the Revolut authentication key (API key/token)
    revolut_authentication_key = fields.Char(
        string="Authentication Key",
        help="API key used to authenticate with Revolut's merchant portal.",
    )

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code not in ['revolut']:
            return default_codes
        return ['revolut']

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """
        Override to exclude Revolut for unsupported currencies.
        Revolut supports only CHF, USD, EUR, and GBP.
        """
        acquirers = super()._get_compatible_acquirers(
            *args, currency_id=currency_id, **kwargs
        )

        currency_model = self.env["res.currency"]
        currency = currency_model.browse(currency_id).exists()
        if currency and currency.name not in ["CHF", "USD", "EUR", "GBP"]:
            acquirers = acquirers.filtered(lambda a: a.provider != "revolut")

        return acquirers

    def get_revolut_base_url(self):
        """
        Return the appropriate base URL for Revolut depending on the provider state.
        - Sandbox URL is used in test mode.
        - Live URL is used in production.
        """
        return (
            "https://sandbox-merchant.revolut.com"
            if self.state == "test"
            else "https://merchant.revolut.com"
        )
