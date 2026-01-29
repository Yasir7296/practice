# payment_revolut/tests/common.py

from odoo.addons.payment.tests.common import PaymentCommon


class RevolutCommon(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Setup Revolut provider with dummy API key
        cls.revolut = cls._prepare_provider(
            "revolut",
            update_values={
                "revolut_authentication_key": "dummy_token",
            },
        )

        cls.provider = cls.revolut
        cls.currency = cls.currency_euro

        # Mocked notification data
        cls.notification_data = {
            "id": "test-payment-id",
            "description": cls.reference,
            "state": "completed",
        }
