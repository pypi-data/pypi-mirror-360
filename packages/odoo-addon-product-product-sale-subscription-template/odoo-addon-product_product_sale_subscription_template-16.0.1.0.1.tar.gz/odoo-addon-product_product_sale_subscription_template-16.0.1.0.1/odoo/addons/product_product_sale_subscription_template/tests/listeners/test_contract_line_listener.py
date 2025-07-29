from datetime import timedelta, date

from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import TransactionCase


class TestContractLineListener(TransactionCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        ComponentMixin.setUp(self)

        self.ContractLine = self.env["contract.line"]
        self.product = self.env.ref("product.product_product_1")

    def test_create_line_product_id_without_subscription_template(self):
        """Test that when a contract line is created with a product_id that does not have
        a subscription template, the date_end is not set."""

        line = self.ContractLine.create(
            {
                "name": "Test",
                "contract_id": 1,  # Assuming a contract with ID 1 exists
                "product_id": self.product.id,
                "date_start": date.today(),
                "recurring_next_date": date.today() + timedelta(days=30),
            }
        )
        self.assertEqual(line.date_start, date.today())
        self.assertFalse(line.date_end)

    def test_create_line_product_id_with_subscription_template(self):
        """Test that when a contract line is created with a product_id related to
        a subscription template, the date_end is set according to the template."""

        today = date.today()
        sale_subscription_template = self.env["sale.subscription.template"].create(
            {
                "name": "Test Template",
                "recurring_rule_type": "months",
                "recurring_rule_boundary": "limited",
                "recurring_rule_count": 12,
                "code": "test_template",
            }
        )

        self.product.write(
            {"sale_subscription_template_id": sale_subscription_template.id}
        )

        line = self.ContractLine.create(
            {
                "name": "Test",
                "contract_id": 1,  # Assuming a contract with ID 1 exists
                "product_id": self.product.id,
                "date_start": today,
                "recurring_next_date": today + timedelta(days=30),
            }
        )
        self.assertEqual(line.date_start, today)
        self.assertEqual(line.date_end, today + timedelta(days=365))
