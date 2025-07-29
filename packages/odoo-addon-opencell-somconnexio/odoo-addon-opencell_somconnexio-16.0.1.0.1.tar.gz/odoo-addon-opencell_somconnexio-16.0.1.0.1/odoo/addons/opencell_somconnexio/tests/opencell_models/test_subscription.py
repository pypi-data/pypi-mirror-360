from odoo.tests.common import TransactionCase
from odoo.addons.somconnexio.tests.factories import PartnerFactory, ContractFactory

from ...opencell_models.subscription import SubscriptionFromContract
from datetime import datetime


class SubscriptionFromContractTestCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.crm_account_code = "1234"

        self.contract = ContractFactory()
        self.contract.code = 1234
        self.contract.phone_number = "666666666"
        self.contract.service_type = "vodafone"
        self.contract.date_start = datetime.strptime("2020-03-11", "%Y-%m-%d")
        self.contract.service_partner_id = PartnerFactory()

    @staticmethod
    def _custom_fields_to_dict(custom_fields):
        custom_fields_dict = {}
        for field in custom_fields:
            custom_fields_dict[field["code"]] = field["stringValue"]

        return custom_fields_dict

    def _common_assert(self, subscription_from_contract, offer_code):
        self.assertEqual(subscription_from_contract.code, 1234)
        self.assertEqual(subscription_from_contract.description, "666666666")
        self.assertEqual(subscription_from_contract.offerTemplate, offer_code)
        self.assertEqual(subscription_from_contract.subscriptionDate, "2020-03-11")

    def _assert_custom_fields(self, subscription_from_contract):
        custom_fields_dict = self._custom_fields_to_dict(
            subscription_from_contract.customFields["customField"]
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_ADDRESS"],
            self.contract.service_partner_id.full_street,
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_CP"],
            self.contract.service_partner_id.zip,
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_CITY"],
            self.contract.service_partner_id.city,
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_SUBDIVISION"],
            self.contract.service_partner_id.state_id.name,
        )

    def test_mobile_subscription_construct_ok(self):
        self.contract.service_contract_type = "mobile"
        self.contract.service_partner_id = None

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )
        self._common_assert(subscription_from_contract, "OF_SC_TEMPLATE_MOB")
        self.assertEqual(subscription_from_contract.customFields, {})

    def test_broadband_subscription_construct_ok(self):
        self.contract.service_contract_type = "vodafone"

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )

        self._common_assert(subscription_from_contract, "OF_SC_TEMPLATE_BA")
        self._assert_custom_fields(subscription_from_contract)

    def test_switchboard_subscription_construct_ok(self):
        self.contract.service_contract_type = "switchboard"
        self.contract.service_partner_id = None

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )
        self._common_assert(subscription_from_contract, "OF_SC_TEMPLATE_CV")
        self.assertEqual(subscription_from_contract.customFields, {})

    def test_filmin_subscription_construct_ok(self):
        self.contract.service_contract_type = "filmin"
        self.contract.service_partner_id = None

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )
        self._common_assert(subscription_from_contract, "OF_SC_TEMPLATE_CT")
        self.assertEqual(subscription_from_contract.customFields, {})
