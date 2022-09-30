# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class payment_terms(models.Model):
    _name = 'payment.terms'

    name = fields.Char(string='Name')
    payment_id = fields.Char(string='ID')
    payment_means_id = fields.Char(string='Método Pago')
    amount = fields.Float(string='Monto')
    date_due = fields.Date(string='Fecha Vencida')
    is_fixed = fields.Boolean(string='Couta Fija')
    invoice_id = fields.Many2one('account.invoice', string='Factura', ondelete='cascade', index=True)
    pos_order_id = fields.Many2one('pos.order', string='Pedido POS', ondelete='cascade', index=True)
    bank_statement_line = fields.Many2one('account.bank.statement.line', string='Estado bancario', ondelete='cascade', index=True)