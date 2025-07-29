To configure the integration between Odoo and OpenCell you need to expose in the Odoo environment the next variables used to access the OpenCell API:

```bash
export OPENCELL_BASEURL="https://opencell.organization.org/"
export OPENCELL_USER="opencell_user"
export OPENCELL_PASSWORD='opencell_password'
```

Then, create and configure the Seller and the Client category in OpenCell and update the Odoo configuration settings `opencell_seller_code` and `opencell_customer_category_code`.

#### Products

To integrate the products between the envrionments, the CODE of the product in OpenCell must exist in Odoo as Product default code of a product.

OpenCell Product Code <==> Odoo Product Default Code
