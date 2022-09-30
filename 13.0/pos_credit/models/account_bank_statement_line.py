# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging
import sys
_logger = logging.getLogger(__name__)

class account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'

    business_transaction_type = fields.Selection(selection=[('without_credit','Débito')], string="Tipo de Transacción" , default='without_credit')
    # fixed: an equals amount for all cuotes
    # not fixed: an agreement between both parties
    fixed_period = fields.Boolean( string="¿Cuota fija?" , default=True )
    payment_terms = fields.One2many( 'payment.terms', 'pos_order_id', string="Términos del pago" )    
    payment_terms_cuotes = fields.Integer( string="Cuotas" , default=1 )
    payment_terms_period = fields.Many2one( 'account.payment.term', string="Término créditicio" )
    credit_percent_charge = fields.Float( string="Cargo (%)" )
    credit_initial_total_amount = fields.Float( string="Monto Inicial" )
    credit_amount_fixed = fields.Float( string="Cargo Periódico" )