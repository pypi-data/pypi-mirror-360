from .opencell_resource import OpenCellResource
from .opencell_types.custom_field import CustomField


class SubscriptionFromContract(OpenCellResource):
    white_list = [
        "code",
        "description",
        "userAccount",
        "offerTemplate",
        "subscriptionDate",
        "customFields",
    ]

    def __init__(self, contract, crm_account_hierarchy_code):
        self.contract = contract
        self.userAccount = crm_account_hierarchy_code

    @property
    def code(self):
        return self.contract.code

    @property
    def description(self):
        return self.contract.phone_number

    @property
    def offerTemplate(self):
        """
        Returns offer template code for current contract's service type.

        :return: offer template code (string)
        """

        if self.contract.service_contract_type == "mobile":
            return "OF_SC_TEMPLATE_MOB"
        elif self.contract.service_contract_type == "switchboard":
            return "OF_SC_TEMPLATE_CV"
        elif self.contract.service_contract_type == "filmin":
            return "OF_SC_TEMPLATE_CT"
        else:
            return "OF_SC_TEMPLATE_BA"

    @property
    def subscriptionDate(self):
        return self.contract.date_start.strftime("%Y-%m-%d")

    @property
    def customFields(self):
        if not self.contract.service_partner_id:
            return {}
        address = self.contract.service_partner_id
        return {
            "customField": [
                CustomField(
                    "CF_OF_SC_SUB_SERVICE_ADDRESS", address.full_street
                ).to_dict(),
                CustomField("CF_OF_SC_SUB_SERVICE_CP", address.zip).to_dict(),
                CustomField("CF_OF_SC_SUB_SERVICE_CITY", address.city).to_dict(),
                CustomField(
                    "CF_OF_SC_SUB_SERVICE_SUBDIVISION", address.state_id.name
                ).to_dict(),
            ]
        }
