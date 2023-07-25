# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal


class Main(CustomerPortal):

    @http.route("/dr_consumer_note", type="http", auth="user", website=True, methods=['POST', 'GET'])
    def consumer_note(self, **post):
        order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order_id')))
        try:
            order_sudo = self._document_check_access('sale.order', order_id.id, access_token=post.get('access_token'))
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError(_("The access token is invalid."))
        if order_id.state != 'sale' and order_sudo.access_token == post.get('access_token'):
            order_id.write({'consumer_note': post.get('consumer_note')})
        return request.redirect('/my/orders/%s' %(order_id.id))
