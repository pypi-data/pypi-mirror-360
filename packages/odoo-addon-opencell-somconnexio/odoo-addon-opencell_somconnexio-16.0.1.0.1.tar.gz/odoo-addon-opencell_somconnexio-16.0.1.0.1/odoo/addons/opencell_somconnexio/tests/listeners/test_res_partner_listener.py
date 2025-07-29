from odoo.addons.component.tests.common import ComponentMixin
from odoo.addons.somconnexio.tests.helper_service import (
    contract_mobile_create_data,
)
from odoo.tests.common import TransactionCase


class TestResPartnerListener(TransactionCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestResPartnerListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self):
        # resolve an inheritance issue (TransactionCase does not call super)
        super().setUp()
        ComponentMixin.setUp(self)
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.env["contract.contract"].create(
            contract_mobile_create_data(self.env, self.partner)
        )

    def test_res_partner_listener_edit_address_field(self):
        queue_jobs_before = self.env["queue.job"].search([])
        self.partner.write({"street": "street test"})
        queue_jobs_after = self.env["queue.job"].search([])
        self.assertEqual(2, len(queue_jobs_after - queue_jobs_before))

    def test_res_partner_listener_edit_not_address_field(self):
        queue_jobs_before = self.env["queue.job"].search([])
        self.partner.write({"name": "test"})
        queue_jobs_after = self.env["queue.job"].search([])
        self.assertEqual(0, len(queue_jobs_after - queue_jobs_before))
