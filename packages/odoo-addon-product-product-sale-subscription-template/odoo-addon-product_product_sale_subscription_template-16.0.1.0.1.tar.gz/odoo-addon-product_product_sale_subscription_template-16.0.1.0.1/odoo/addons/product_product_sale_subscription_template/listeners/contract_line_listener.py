from odoo.addons.component.core import Component


class ContractLineListener(Component):
    _name = "multimedia.contract.line.listener"
    _inherit = "base.event.listener"
    _apply_on = ["contract.line"]

    def on_record_create(self, record, fields=None):
        subscription_template = record.product_id.sale_subscription_template_id
        if subscription_template.exists():
            self._set_expiration_date_to_line(record, subscription_template)

    def _set_expiration_date_to_line(self, record, subscription_template):
        """
        Set the date_end of the contract line based on the sale.subscription.template
        duration.
        Parameters:
            record (contract.line): The contract line record.
            subscription_template (sale.subscription.template):
                The subscription template associated with the product.
        """

        date_start = record.date_start
        if not date_start:
            return

        date_end = subscription_template._get_date(date_start)

        record.write({"date_end": date_end})
