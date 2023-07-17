# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Main(http.Controller):

    @http.route("/dr_consumer_note", type="http", auth="user", website=True, methods=['POST'])
    def consumer_note(self,**post):
        if post.get('sale_order_id'):
            order_id = request.env['sale.order'].browse(int(post.get('sale_order_id')))
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",order_id.state)
            if order_id.state != 'sale':
                order_id.write({'consumer_note': post.get('consumer_note')})
        return request.redirect('/my/home')
