from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.tests.helper_service import (
    partner_create_data,
)

from mock import patch, Mock


class TestResPartner(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.parent_partner = self.env["res.partner"].create(
            {
                "name": "test",
                "vat": "ES00470223B",
                "country_id": self.ref("base.es"),
            }
        )

    @patch("odoo.addons.opencell_somconnexio.models.res_partner.Customer.get")  # noqa
    def test_update_customer_one_customer_account(self, CustomerGetMock):  # noqa
        partner_vals = partner_create_data(self)
        partner_vals.update(
            {
                "parent_id": self.parent_partner.id,
                "type": "contract-email",
            }
        )
        partner = self.env["res.partner"].create(partner_vals)
        oc_code = "1234_1"
        self.assertTrue(partner)
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = partner.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [{"code": oc_code}]
        }

        def side_effect_customer_get(code):
            if code == partner.ref:
                return mock_customer

        CustomerGetMock.side_effect = side_effect_customer_get
        queue_jobs_before = self.env["queue.job"].search([])
        partner.with_context(test_queue_job_no_delay=False).update_accounts_address()
        queue_jobs_after = self.env["queue.job"].search([])
        self.assertEqual(1, len(queue_jobs_after - queue_jobs_before))
        CustomerGetMock.assert_called_once_with(partner.ref)

    @patch("odoo.addons.opencell_somconnexio.models.res_partner.Customer.get")  # noqa
    def test_update_customer_many_customer_account(self, CustomerGetMock):  # noqa
        partner_vals = partner_create_data(self)
        partner_vals.update(
            {
                "parent_id": self.parent_partner.id,
                "type": "contract-email",
            }
        )
        partner = self.env["res.partner"].create(partner_vals)
        oc_codes = ["1234_1", "1234_2"]
        self.assertTrue(partner)
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = partner.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [{"code": oc_codes[0]}, {"code": oc_codes[1]}]
        }

        def side_effect_customer_get(code):
            if code == partner.ref:
                return mock_customer

        CustomerGetMock.side_effect = side_effect_customer_get
        queue_jobs_before = self.env["queue.job"].search([])
        partner.with_context(test_queue_job_no_delay=False).update_accounts_address()
        queue_jobs_after = self.env["queue.job"].search([])
        self.assertEqual(2, len(queue_jobs_after - queue_jobs_before))
        CustomerGetMock.assert_called_once_with(partner.ref)

    @patch(
        "odoo.addons.opencell_somconnexio.models.res_partner.CRMAccountHierarchyFromPartnerUpdateService"  # noqa
    )
    def test_update_subscription(self, CRMAccountFromPartnerMock):
        partner_vals = partner_create_data(self)
        partner_vals.update(
            {
                "parent_id": self.parent_partner.id,
                "type": "contract-email",
            }
        )
        partner = self.env["res.partner"].create(partner_vals)
        oc_code = "1234_1"

        partner.update_subscription("address", oc_code)

        CRMAccountFromPartnerMock.assert_called_once_with(partner, "address", oc_code)
        CRMAccountFromPartnerMock.return_value.run.assert_called()

    def test_default_block_contract_creation_in_OC(self):
        self.assertFalse(self.parent_partner.block_contract_creation_in_OC)
