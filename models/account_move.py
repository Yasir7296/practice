from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    revolut_payment_url = fields.Char(
        string="Revolut Payment Link",
        compute="_compute_revolut_payment_url",
        help="URL for customers to complete the payment via Revolut",
    )

    def _compute_revolut_payment_url(self):
        """
        Compute the Revolut payment URL for each invoice.
        It searches for a pending or draft Revolut transaction
        matching the invoice name and sets the corresponding API URL.
        """
        for invoice in self:
            invoice.revolut_payment_url = (
                False
            )  # Default to False if no transaction found
            transaction = self.env["payment.transaction"].search(
                [
                    ("reference", "=", invoice.name),
                    ("provider", "=", "revolut"),
                    ("state", "in", ["draft", "pending"]),
                ],
                limit=1,
            )

            if transaction:
                rendering_values = transaction._get_specific_rendering_values(
                    {
                        "amount": invoice.amount_total,
                        "currency": invoice.currency_id.name,
                    }
                )
                invoice.revolut_payment_url = rendering_values.get("api_url")
