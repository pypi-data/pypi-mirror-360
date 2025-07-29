from mock import Mock, patch
from datetime import date

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.tests.helper_service import (
    contract_mobile_create_data,
)


class TestContractCompensationWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.contract = self.env["contract.contract"].create(
            contract_mobile_create_data(self.env, self.partner)
        )
        product = self.browse_ref("somconnexio.SenseMinuts1GB")
        contract_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": "2020-01-01 00:00:00",
        }
        self.contract.contract_line_ids = [(0, 0, contract_line)]

        pricelist_item = self.browse_ref(
            "somconnexio.pricelist_without_IVA"
        ).item_ids.filtered(lambda i: i.product_id == product)
        self.price = pricelist_item.fixed_price
        self.days_without_service = 2.0

    @patch(
        "odoo.addons.opencell_somconnexio.wizards.contract_compensation.contract_compensation.SubscriptionService",  # noqa
        return_value=Mock(spec=["create_one_shot"]),
    )
    def test_compensate_days_without_service_active_contract(self, SubscriptionService):
        amount_to_compensate = round((self.days_without_service * self.price / 30), 4)
        create_one_shot = SubscriptionService.return_value.create_one_shot
        wizard = (
            self.env["contract.compensation.wizard"]
            .with_context(active_id=self.partner.id)
            .create(
                {
                    "contract_ids": [(6, 0, [self.contract.id])],
                    "partner_id": self.partner.id,
                    "type": "days_without_service",
                    "days_without_service": self.days_without_service,
                }
            )
        )
        wizard.button_compensate()
        self.assertEqual(
            round(wizard.days_without_service_import, 4), amount_to_compensate
        )
        wizard.description = "Test description"
        wizard.operation_date = date(2021, 5, 15)
        wizard.opencell_compensate()
        create_one_shot.assert_called_once_with(
            "CH_SC_OSO_COMPENSATION",
            -amount_to_compensate,
            description="Test description",
            operation_date=date(2021, 5, 15),
        )
