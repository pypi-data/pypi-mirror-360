from datetime import date

from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import TransactionCase

from odoo.addons.somconnexio.tests.helper_service import (
    contract_mobile_create_data,
)


class TestContractListener(TransactionCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestContractListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        ComponentMixin.setUp(self)

        self.partner = self.env.ref("somconnexio.res_partner_2_demo")
        self.contract_data = contract_mobile_create_data(self.env, self.partner)

    def test_create(self):
        contract = self.env["contract.contract"].create(self.contract_data)

        jobs_domain = [
            ("method_name", "=", "create_subscription"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [contract.id])

    def test_terminate(self):
        contract = self.env["contract.contract"].create(self.contract_data)
        self.env['contract.line'].create({
            'name': 'test',
            'contract_id': contract.id,
            'product_id': self.ref('somconnexio.contract_mobile_t_conserva'),
            'quantity': 1,
            'price_unit': 10.0,
            'date_start': date.today(),
        })
        # Listener would be activated when date_end is set
        contract.date_end = date.today()
        contract.terminate_contract(
            self.browse_ref("somconnexio.reason_other"),
            "Comment",
            date.today(),
            self.browse_ref("somconnexio.user_reason_other"),
        )

        jobs_domain = [
            ("method_name", "=", "terminate_subscription"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [contract.id])
