from odoo import models

from ..opencell_services.crm_account_hierarchy_create_service import (
    CRMAccountHierarchyFromContractCreateService,
)
from ..opencell_services.crm_account_hierarchy_update_service import (
    CRMAccountHierarchyFromContractUpdateService,
)
from ..opencell_services.subscription_service import SubscriptionService
from .opencell_configuration import OpenCellConfiguration


class Contract(models.Model):
    _inherit = "contract.contract"

    def create_subscription(self, _id, force=False):
        contract = self.browse(_id)
        CRMAccountHierarchyFromContractCreateService(
            contract,
            OpenCellConfiguration(self.env),
        ).run(force=force)

    def terminate_subscription(self, _id):
        contract = self.browse(_id)
        SubscriptionService(contract).terminate()

    def update_subscription(self, contracts, updated_field):
        CRMAccountHierarchyFromContractUpdateService(contracts, updated_field).run()

    def update_subscription_force(self, contracts, updated_field):
        CRMAccountHierarchyFromContractUpdateService(
            contracts, updated_field, force=True
        ).run()

    def add_one_shot(self, _id, product_default_code):
        contract = self.browse(_id)
        SubscriptionService(contract).create_one_shot(product_default_code)

    def add_service(self, _id, contract_line):
        contract = self.browse(_id)
        SubscriptionService(contract).create_service(contract_line)

    def terminate_service(self, _id, contract_line):
        contract = self.browse(_id)
        SubscriptionService(contract).terminate_service(
            contract_line.product_id, contract_line.date_end
        )
