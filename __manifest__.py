{
    # Basic module information
    "name": "Revolut Payment Acquirer",
    "summary": "Payment Acquirer: Revolut Payment Implementation",
    "version": "17.0.1.0.2",
    "category": "Accounting/Payment",
    # Module dependencies
    "depends": ["payment", "sale", "website_sale"],
    # Data and views to load
    "data": [
        "views/payment_revolut_template.xml",  # QWeb redirect form
        "data/payment_provider_data.xml",  # Payment provider and method records
        "views/revolut_view.xml",  # Provider configuration form view
    ],
    "images": ["static/description/Revolut_payment.gif"],
    # Hook methods
    "uninstall_hook": "uninstall_hook",  # Cleans up configuration on module uninstall
    # Licensing and authorship
    "license": "OPL-1",
    "author": "Synodica Solutions Pvt. Ltd.",
    "maintainer": "Synodica Solutions Pvt. Ltd.",
    "website": "https://synodica.com",
    # Technical flags
    "installable": True,
    "auto_install": False,
    "application": True,

    "price": "199.00",
    "currency": "USD",
}
