# payment_revolut/tests/test_revolut.py

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment_revolut.tests.common import RevolutCommon


@tagged("post_install", "-at_install")
class RevolutTest(RevolutCommon):
    def test_revolut_rendering_values(self):
        """Test that Revolut returns a valid rendering dict with an api_url."""
        tx = self._create_transaction(flow="redirect")

        with patch(
            "odoo.addons.payment_revolut.models.payment_transaction.requests.post"
        ) as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                "id": "test-payment-id",
                "checkout_url": "https://revolut.mock/checkout",
                "amount": 111111,
                "currency": "EUR",
                "description": tx.reference,
            }

            rendering = tx._get_specific_rendering_values(
                {
                    "amount": tx.amount,
                    "currency": tx.currency_id.name,
                    "reference": tx.reference,
                }
            )

        self.assertIn("api_url", rendering)
        self.assertEqual(rendering["api_url"], "https://revolut.mock/checkout")

    @mute_logger("odoo.addons.payment_revolut.models.payment_transaction")
    def test_webhook_notification_confirms_transaction(self):
        """Simulate a Revolut webhook marking the payment as done."""
        tx = self._create_transaction(flow="redirect")
        tx.provider_reference = "test-payment-id"

        # Call the internal validation directly
        tx._process_notification_data(self.notification_data)
        self.assertEqual(tx.state, "done")
