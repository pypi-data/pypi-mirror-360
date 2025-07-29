import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_subscription_menu_invisible(env)


def set_subscription_menu_invisible(env):
    """Archive subscription menu."""
    menu = env.ref("subscription_oca.sale_subscription_root", raise_if_not_found=False)
    if menu:
        menu.write({"active": False})
        _logger.info("Subscription menu archived successfully")
    else:
        _logger.warning("Subscription menu not found, nothing to do")
