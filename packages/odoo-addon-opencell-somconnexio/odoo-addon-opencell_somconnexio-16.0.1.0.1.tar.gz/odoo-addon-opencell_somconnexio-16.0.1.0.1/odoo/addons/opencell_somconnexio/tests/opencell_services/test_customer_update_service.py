from odoo.tests import TransactionCase
from mock import Mock, patch
from ...opencell_services.customer_update_service import (
    CustomerFromPartnerUpdateService,
)
from ...opencell_services.opencell_exceptions import PyOpenCellException
from odoo.addons.somconnexio.tests.factories import PartnerFactory

from ..factory import OpenCellConfigurationFactory


class CustomerUpdateServiceTests(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = PartnerFactory()
        self.opencell_configuration = OpenCellConfigurationFactory()

    @patch(
        "odoo.addons.opencell_somconnexio.opencell_services.customer_update_service.Customer",  # noqa
        spec=["update"],
    )
    @patch(
        "odoo.addons.opencell_somconnexio.opencell_services.customer_update_service.CustomerFromPartner",  # noqa
        return_value=Mock(spec=["to_dict"]),
    )
    def test_update_from_customer_from_partner_ok(
        self,
        MockCustomerFromPartner,
        MockCustomer,
    ):
        MockCustomerFromPartner.return_value.to_dict.return_value = {
            "example_data": 123
        }

        CustomerFromPartnerUpdateService(
            self.partner, self.opencell_configuration
        ).run()

        MockCustomerFromPartner.assert_called_with(
            self.partner, self.opencell_configuration
        )
        MockCustomer.update.assert_called_with(
            **MockCustomerFromPartner.return_value.to_dict.return_value
        )

    @patch(
        "odoo.addons.opencell_somconnexio.opencell_services.customer_update_service.Customer",  # noqa
        spec=["update"],
    )
    @patch(
        "odoo.addons.opencell_somconnexio.opencell_services.customer_update_service.CustomerFromPartner",  # noqa
        return_value=Mock(spec=["to_dict"]),
    )
    def test_update_from_customer_from_partner_exception_oc(
        self,
        MockCustomerFromPartner,
        MockCustomer,
    ):
        MockCustomerFromPartner.return_value.to_dict.return_value = {
            "example_data": 123
        }
        MockCustomer.update.side_effect = Exception()
        service = CustomerFromPartnerUpdateService(
            self.partner, self.opencell_configuration
        )
        self.assertRaises(
            PyOpenCellException,
            service.run,
        )
