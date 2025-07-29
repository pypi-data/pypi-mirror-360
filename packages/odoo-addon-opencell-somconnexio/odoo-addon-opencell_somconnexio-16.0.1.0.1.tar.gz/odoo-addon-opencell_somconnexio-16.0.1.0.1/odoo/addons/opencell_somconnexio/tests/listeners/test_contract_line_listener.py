from odoo import fields
from datetime import timedelta
from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import TransactionCase


class TestContractLineListener(TransactionCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestContractLineListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        ComponentMixin.setUp(self)

        self.ContractLine = self.env["contract.line"]
        self.ba_service = self.browse_ref("somconnexio.Fibra600Mb")
        self.mobile_service = self.browse_ref("somconnexio.SenseMinutsSenseDades")
        self.ba_one_shot = self.browse_ref("somconnexio.AltaParellExistent")
        self.switchboard_service = self.browse_ref(
            "switchboard_somconnexio.AgentCentraletaVirtualApp500"
        )
        self.filmin_service = self.browse_ref("filmin_somconnexio.FilminSubscription")
        self.sports_service = self
        self.router_return_one_shot = self.browse_ref("somconnexio.EnviamentRouter")
        self.mobile_one_shot = self.browse_ref("somconnexio.DadesAddicionals500MB")
        self.international_mins = self.browse_ref("somconnexio.Internacional100Min")
        self.ip_fixa = self.browse_ref("somconnexio.IPv4Fixa")

        self.ba_contract = self.env.ref("somconnexio.contract_fibra_600")
        self.mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.switchboard_contract = self.env.ref(
            "switchboard_somconnexio.contract_switchboard_app_500"
        )
        self.filmin_contract = self.env.ref("filmin_somconnexio.contract_filmin")

        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")

        self.router_4G_contract_service_info = self.env[
            "router.4g.service.contract.info"
        ].create(
            {
                "phone_number": "654321123",
                "vodafone_id": "123",
                "vodafone_offer_code": "456",
                "icc": "2222",
            }
        )
        self.router_4g_contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract 4G",
                "partner_id": self.partner.id,
                "service_partner_id": self.partner.id,
                "invoice_partner_id": self.partner.id,
                "service_technology_id": self.ref("somconnexio.service_technology_4G"),
                "service_supplier_id": self.ref(
                    "somconnexio.service_supplier_vodafone"
                ),
                "router_4G_service_contract_info_id": (
                    self.router_4G_contract_service_info.id
                ),
                "mandate_id": self.partner.bank_ids[0].mandate_ids[0].id,
                "email_ids": [(6, 0, [self.partner.id])],
            }
        )

    def test_create_line_with_mobile_service(self):
        cl = self.ContractLine.create(
            {
                "name": self.mobile_service.name,
                "contract_id": self.mobile_contract.id,
                "product_id": self.mobile_service.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [self.mobile_contract.id, cl])

    def test_create_line_with_ba_service(self):
        cl = self.ContractLine.create(
            {
                "name": self.ba_service.name,
                "contract_id": self.ba_contract.id,
                "product_id": self.ba_service.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [self.ba_contract.id, cl])

    def test_create_line_with_filmin_service(self):
        cl = self.ContractLine.create(
            {
                "name": self.filmin_service.name,
                "contract_id": self.filmin_contract.id,
                "product_id": self.filmin_service.id,
                "date_start": fields.Date.today() - timedelta(days=15),
            }
        )
        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [self.filmin_contract.id, cl])

    def test_create_line_with_switchboard_service(self):
        cl = self.ContractLine.create(
            {
                "name": self.switchboard_service.name,
                "contract_id": self.switchboard_contract.id,
                "product_id": self.switchboard_service.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [self.switchboard_contract.id, cl])

    def test_create_line_with_mobile_one_shot(self):
        self.ContractLine.create(
            {
                "name": self.mobile_one_shot.name,
                "contract_id": self.mobile_contract.id,
                "product_id": self.mobile_one_shot.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_one_shot"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(
            queued_jobs.args,
            [
                self.mobile_contract.id,
                self.mobile_one_shot.default_code,
            ],
        )

    def test_create_line_with_ba_one_shot(self):
        self.ContractLine.create(
            {
                "name": self.ba_one_shot.name,
                "contract_id": self.ba_contract.id,
                "product_id": self.ba_one_shot.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_one_shot"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(
            queued_jobs.args, [self.ba_contract.id, self.ba_one_shot.default_code]
        )

    def test_create_line_with_router_return_one_shot(self):
        self.ContractLine.create(
            {
                "name": self.router_return_one_shot.name,
                "contract_id": self.router_4g_contract.id,
                "product_id": self.router_return_one_shot.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_one_shot"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(
            queued_jobs.args,
            [self.router_4g_contract.id, self.router_return_one_shot.default_code],
        )

    def test_create_line_with_ba_additional_service(self):
        cl = self.ContractLine.create(
            {
                "name": self.ip_fixa.name,
                "contract_id": self.ba_contract.id,
                "product_id": self.ip_fixa.id,
                "date_start": fields.Date.today(),
            }
        )

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [self.ba_contract.id, cl])

    def test_terminate_line_enqueue_terminate_service(self):
        cl = self.ContractLine.create(
            {
                "name": self.ip_fixa.name,
                "contract_id": self.ba_contract.id,
                "product_id": self.ip_fixa.id,
                "date_start": fields.Date.today(),
            }
        )
        cl.write({"date_end": fields.Date.today()})

        jobs_domain = [
            ("method_name", "=", "terminate_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env["queue.job"].search(jobs_domain)

        self.assertEqual(1, len(queued_jobs))
        self.assertEqual(queued_jobs.args, [self.ba_contract.id, cl])
