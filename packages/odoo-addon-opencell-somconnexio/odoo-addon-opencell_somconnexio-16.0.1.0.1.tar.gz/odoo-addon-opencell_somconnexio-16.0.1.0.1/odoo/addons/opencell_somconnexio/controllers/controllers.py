import base64

from odoo import http

from odoo.addons.web.controllers.main import content_disposition
from odoo.http import serialize_exception as _serialize_exception
import functools
import werkzeug
import json
from pyopencell.client import Client
from pyopencell.exceptions import PyOpenCellAPIException


import logging
_logger = logging.getLogger()


def serialize_exception(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            _logger.exception("An exception occured during an http request")
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))
    return wrap


class UserController(http.Controller):
    @http.route(
        ["/web/binary/download_invoice"], auth="user", methods=["GET"], website=False
    )
    @serialize_exception
    def download_invoice(self, invoice_number, **kw):
        try:
            invoice_response = Client().get(
                "/invoice", invoiceNumber=invoice_number, includePdf=True
            )
        except PyOpenCellAPIException:
            return http.request.not_found()
        invoice_base64 = invoice_response["invoice"]["pdf"]
        filecontent = base64.b64decode(invoice_base64)
        if not filecontent:
            return http.request.not_found()
        else:
            filename = "{}.pdf".format(invoice_number)
            return http.request.make_response(
                filecontent,
                [
                    ("Content-Type", "application/octet-stream"),
                    ("Content-Disposition", content_disposition(filename)),
                ],
            )
