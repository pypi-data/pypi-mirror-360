from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_subscription_template_id = fields.Many2one(
        comodel_name="sale.subscription.template",
        string="Subscription Template",
        help="Subscription template to use for this product.",
    )
