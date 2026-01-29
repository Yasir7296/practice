from odoo import api, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    @api.model
    def _get_payment_method_information(self):
        """
        Extend the base method to add support for the custom
        'Revolut' payment method.

        - Sets the mode to 'unique', meaning it can only be
        used in one journal at a time.
        - Restricts usage to journals of type 'bank' using the domain.
        """
        res = super()._get_payment_method_information()
        res["revolut"] = {
            "mode": "unique",
            "domain": [("type", "=", "bank")],
        }
        return res
