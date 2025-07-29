from odoo import models, fields

from pyopencell.resources.customer import Customer
from ..opencell_services.crm_account_hierarchy_update_service import (
    CRMAccountHierarchyFromPartnerUpdateService,
)
from ..opencell_services.customer_update_service import CustomerFromPartnerUpdateService
from ...opencell_somconnexio.models.opencell_configuration import OpenCellConfiguration


class ResPartner(models.Model):
    _inherit = "res.partner"

    block_contract_creation_in_OC = fields.Boolean(
        string="Block concract creation in OC?",
        store=True,
        default=False,
        help="No permetre la creació automàtica de subscripcions a OpenCell. S'entraràn manualment",  # noqa
    )

    def update_accounts_address(self):
        customer = Customer.get(self.ref).customer
        customer_accounts = customer.customerAccounts["customerAccount"]
        for customer_account_code in [ca.get("code") for ca in customer_accounts]:
            self.with_delay().update_subscription("address", customer_account_code)

    def update_subscription(self, updated_field, customer_account_code):
        CRMAccountHierarchyFromPartnerUpdateService(
            self, updated_field, customer_account_code
        ).run()

    def update_customer(self):
        CustomerFromPartnerUpdateService(self, OpenCellConfiguration(self.env)).run()
