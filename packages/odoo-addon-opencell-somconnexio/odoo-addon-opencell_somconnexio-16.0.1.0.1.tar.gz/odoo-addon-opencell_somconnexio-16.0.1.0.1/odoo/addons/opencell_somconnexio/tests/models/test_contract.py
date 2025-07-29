from mock import Mock, patch

from odoo.addons.somconnexio.tests.helper_service import (
    contract_fiber_create_data,
    contract_adsl_create_data,
    contract_mobile_create_data,
    contract_4g_create_data,
)
from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase


@patch("odoo.addons.opencell_somconnexio.models.contract.OpenCellConfiguration")
@patch("odoo.addons.opencell_somconnexio.models.contract.SubscriptionService")
@patch(
    "odoo.addons.opencell_somconnexio.models.contract.CRMAccountHierarchyFromContractCreateService"  # noqa
)
@patch(
    "odoo.addons.opencell_somconnexio.models.contract.CRMAccountHierarchyFromContractUpdateService"  # noqa
)
class TestContract(SCComponentTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.service_partner = self.env["res.partner"].create(
            {"parent_id": self.partner.id, "name": "Service partner", "type": "service"}
        )
        self.router_4g_contract_data = contract_4g_create_data(self.env, self.partner)
        self.adsl_contract_data = contract_adsl_create_data(self.env, self.partner)
        self.fiber_contract_data = contract_fiber_create_data(self.env, self.partner)
        self.mobile_contract_data = contract_mobile_create_data(self.env, self.partner)
        self.adsl_contract_service_info = self.env["adsl.service.contract.info"].browse(
            self.adsl_contract_data["adsl_service_contract_info_id"]
        )
        self.router_product = self.adsl_contract_service_info.router_product_id
        self.router_lot = self.adsl_contract_service_info.router_lot_id
        self.vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].browse(self.fiber_contract_data["vodafone_fiber_service_contract_info_id"])
        self.mobile_contract_service_info = self.env[
            "mobile.service.contract.info"
        ].browse(self.mobile_contract_data["mobile_contract_service_info_id"])

    def test_contact_create_call_opencell_integration(
        self,
        _,
        CRMAccountHierarchyFromContractCreateServiceMock,
        __,
        OpenCellConfigurationMock,
    ):
        vals_contract = self.fiber_contract_data
        CRMAccountHierarchyFromContractCreateServiceMock.return_value = Mock(
            spec=["run"]
        )
        OpenCellConfigurationMock.return_value = object

        contract = self.Contract.create(vals_contract)

        CRMAccountHierarchyFromContractCreateServiceMock.assert_called_once_with(
            contract, OpenCellConfigurationMock.return_value
        )
        CRMAccountHierarchyFromContractCreateServiceMock.return_value.run.assert_called_once_with(  # noqa
            force=False
        )
