from odoo import models


class PartnerEmailChangeWizard(models.TransientModel):
    _inherit = "partner.email.change.wizard"

    def button_change(self):
        super().button_change()
        if self.change_contracts_emails == "yes":
            self._enqueue_OC_email_update(self.contract_ids)
        return True

    def _enqueue_OC_email_update(self, contracts):
        self.env["contract.contract"].with_delay(
            priority=50,
        ).update_subscription(contracts, "email")
