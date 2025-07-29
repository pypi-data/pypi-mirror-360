{
    "version": "16.0.1.0.1",
    "name": "Opencell Integration - SomConnexio",
    "summary": """
    Synchronize the needed objects to invoicing from OpenCell.
    Reproduce the next models:
    * Customer (ResPartner)
    * Contract (Contract)
    * Service (Product)
    * Access (Contract ISP Info)
    """,
    "author": """
        Som Connexió SCCL,
        Coopdevs Treball SCCL
    """,
    "category": "Cooperative Management",
    "website": "https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio",
    "license": "AGPL-3",
    "depends": [
        "switchboard_somconnexio",
        "filmin_somconnexio",
        "somconnexio",
        "component",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "wizards/contract_compensation/contract_compensation.xml",
        "wizards/contract_force_oc_integration/contract_force_oc_integration.xml",
        "wizards/contract_iban_change_force/contract_iban_change_force.xml",
    ],
    "demo": [],
    "external_dependencies": {
        "python": [
            "faker",
            "pyopencell",
        ],
    },
    "application": False,
    "installable": True,
}
