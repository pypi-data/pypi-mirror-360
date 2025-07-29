from odoo import models


class ContractIbanChangeWizard(models.TransientModel):
    _inherit = "contract.iban.change.wizard"

    def button_change(self):
        self.ensure_one()
        super().button_change()
        self.enqueue_OC_iban_update()
        return True

    def enqueue_OC_iban_update(self):
        self.env["contract.contract"].with_delay().update_subscription(
            self.contract_ids, "iban"
        )
