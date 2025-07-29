from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.tests.factories import PartnerFactory

from ...opencell_models.opencell_types.address import (
    Address,
)


class OpenCellAddressTypeTests(SCTestCase):
    def test_dict_format(self):
        odoo_partner = PartnerFactory()

        expected_address_format = {
            "address1": odoo_partner.full_street,
            "zipCode": odoo_partner.zip,
            "city": odoo_partner.city,
            "state": odoo_partner.state_id.name,
            "country": odoo_partner.country_id.code,
        }

        address = Address(
            address=odoo_partner.full_street,
            _zip=odoo_partner.zip,
            city=odoo_partner.city,
            state=odoo_partner.state_id.name,
            country=odoo_partner.country_id.code,
        )

        self.assertEqual(expected_address_format, address.to_dict())
