This module is a part of SomConnexió original module.

We are working to separate the monolitic original module in small modules splited by functionalities.

This module manage the integration between Odoo an OpenCell.

OpenCell is the billing system used in Som Connexió. We use this module to synchronize the customers and contracts from Odoo to OpenCell and to import the invoices from OpenCell to Odoo.

Using listeners, we observe the contract and res_partner models and if a new is created or is updated with a field related with the invoice process, a job is generated to call OpenCell to create or update the related object, using the reference of Odoo as identifier in OpenCell.

Objects integrated (Odoo -> OpenCell):

* ResPartner -> Customer / CRMAccountHierarchy
* Contract -> Subscription
* ContractInfo (ISP Info) -> Access
* Product -> Service / OneShot
