from . import 
from . import controllers
from odoo.addons.payment import reset_payment_provider


def uninstall_hook(env):
    """
    Uninstall hook to clean up Revolut payment provider configuration.

    This function is called automatically when the module is uninstalled.
    It removes any links or settings related to the 'revolut' provider
    using Odoo's built-in reset logic for payment providers.

    :param env: Odoo environment passed during module uninstall
    """
    reset_payment_provider(env, "revolut")
this is a testing code .............................
