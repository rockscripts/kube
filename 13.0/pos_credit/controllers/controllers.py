# -*- coding: utf-8 -*-
from odoo import http

# class FlexiretailCredit(http.Controller):
#     @http.route('/pos_credit/pos_credit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_credit/pos_credit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_credit.listing', {
#             'root': '/pos_credit/pos_credit',
#             'objects': http.request.env['pos_credit.pos_credit'].search([]),
#         })

#     @http.route('/pos_credit/pos_credit/objects/<model("pos_credit.pos_credit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_credit.object', {
#             'object': obj
#         })