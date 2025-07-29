from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from ...opencell_services.subscription_service import SubscriptionService


class ContractCompensationWizard(models.TransientModel):
    _inherit = "contract.compensation.wizard"

    is_opencell_compensation = fields.Boolean(
        "Compensation to Open Cell?", compute="_compute_is_opencell_compensation"
    )

    @api.depends("contract_ids")
    def _compute_is_opencell_compensation(self):
        self.is_opencell_compensation = not self.contract_ids.is_terminated

    def opencell_compensate(self):
        compensation_code = "CH_SC_OSO_COMPENSATION"
        amount_without_taxes = round(self.days_without_service_import, 4)
        SubscriptionService(self.contract_ids).create_one_shot(
            compensation_code,
            -amount_without_taxes,
            description=self.description,
            operation_date=self.operation_date,
        )
        message = _(
            "A compensation line has been created in Open Cell with {} €"
        ).format(amount_without_taxes)
        return {
            "name": "Message",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "custom.pop.message",
            "target": "new",
            "context": {"default_name": message},
        }

    def button_compensate(self):
        result = super().button_compensate()
        if self.type == "days_without_service":
            if self.days_without_service <= 0.0:
                raise ValidationError(
                    _("The amount of days without service must be greater than zero")
                )
            tariff_product = self.product_id
            pricelist = self.env["product.pricelist"].search([("code", "=", "0IVA")])
            amount = (
                pricelist._compute_price_rule(tariff_product, 1)[tariff_product.id][0]
                / 30.0
                * self.days_without_service
            )
            if self.is_opencell_compensation:
                self.state = "details"
                self.days_without_service_import = amount
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "contract.compensation.wizard",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": self.id,
                    "views": [(False, "form")],
                    "target": "new",
                }
        return result
