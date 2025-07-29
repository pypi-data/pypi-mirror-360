import mock
from odoo.tests.common import TransactionCase
from ..factory import OpenCellConfigurationFactory
from ...models.opencell_configuration import (
    OpenCellConfiguration,
    OpenCellConfigurationWrapper,
)


class OpenCellConfigurationWrapperTests(TransactionCase):
    def test_get_configurarion_gets_expected_tryton_model(self):
        env_mock = mock.MagicMock()
        wrapper = OpenCellConfigurationWrapper(env_mock)
        wrapper.get_configuration()
        env_mock.__getitem__.assert_called_with("ir.config_parameter")


class ExpectedOpenCellConfigurationWrapper:
    def __init__(self, *args):
        self.configuration = OpenCellConfigurationFactory()
        self.configuration.get_param = lambda p: (
            self.configuration.seller_code
            if p == "opencell_somconnexio.opencell_seller_code"
            else self.configuration.customer_category_code
        )

    def get_configuration(self):
        return self.configuration


class OpenCellConfigurationTests(TransactionCase):
    def setUp(self):
        super().setUp()
        with mock.patch(
            "odoo.addons.opencell_somconnexio.models."
            "opencell_configuration.OpenCellConfigurationWrapper",
            ExpectedOpenCellConfigurationWrapper,
        ):
            self.opencell_configuration = OpenCellConfiguration(mock.ANY)

    def test_seller_code(self):
        self.assertEqual(
            self.opencell_configuration.seller_code,
            self.opencell_configuration.configuration_wrapper.get_configuration().seller_code,  # noqa
        )

    def test_customer_category_code(self):
        self.assertEqual(
            self.opencell_configuration.customer_category_code,
            self.opencell_configuration.configuration_wrapper.get_configuration().customer_category_code,  # noqa
        )


class OpencellIrConfigParameters(TransactionCase):
    def setUp(self):
        super().setUp()
        self.opencell_configuration = OpenCellConfiguration(self.env)

    def test_seller_code(self):
        self.assertEqual(self.opencell_configuration.seller_code, "SC")

    def test_customer_category_code(self):
        self.assertEqual(self.opencell_configuration.customer_category_code, "CLIENT")
