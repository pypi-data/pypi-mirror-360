from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import TransactionCase


class TestPartnerEmailChangeWizard(TransactionCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerEmailChangeWizard, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        ComponentMixin.setUp(self)
        self.partner = self.env.ref("somconnexio.res_partner_1_demo")
        self.contract = self.env.ref("somconnexio.contract_mobile_t_conserva")
        self.partner_email_b = self.env["res.partner"].create(
            {
                "name": "Email b",
                "email": "email_b@example.org",
                "type": "contract-email",
                "parent_id": self.partner.id,
            }
        )
        self.user_admin = self.browse_ref("base.user_admin")

    def test_change_contracts_emails_enqueue_OC_integration(self):
        wizard = (
            self.env["partner.email.change.wizard"]
            .with_context(active_id=self.partner.id)
            .create(
                {
                    "change_contact_email": "no",
                    "change_contracts_emails": "yes",
                    "contract_ids": [(6, 0, [self.contract.id])],
                    "email_ids": [(6, 0, [self.partner_email_b.id])],
                }
            )
        )
        jobs_domain = [
            ("method_name", "=", "update_subscription"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs_before = self.env["queue.job"].search(jobs_domain)
        wizard.button_change()
        queued_jobs_after = self.env["queue.job"].search(jobs_domain)
        queue_job = queued_jobs_after - queued_jobs_before

        self.assertEqual(1, len(queue_job))
        self.assertEqual(queue_job.args, [self.contract, "email"])
