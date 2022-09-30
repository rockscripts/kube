# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging
import sys
_logger = logging.getLogger(__name__)

class pos_order(models.Model):
    _inherit = 'pos.order'

    business_transaction_type = fields.Selection(selection=[('without_credit','Débito')], string="Tipo de Transacción" , default='without_credit')
    fixed_period = fields.Boolean( string="¿Cuota fija?" , default=True )

    def populate_credit_form(self, pos_config_id):
        data = { 'account_payment_terms_list':None, 'period_max_range': None}
        account_payment_terms = self.env['account.payment.term'].sudo().search([])
        account_payment_terms_list = []
        for account_payment_term in  account_payment_terms:
            for line_id in account_payment_term.line_ids:
                item = {'id': account_payment_term.id, 'name': account_payment_term.name, 'days': line_id.days, 'option': line_id.option, }
                account_payment_terms_list.append(item)

        pos_config = self.env['pos.config'].sudo().browse( int(pos_config_id) )
        data['period_max_range'] = pos_config.payment_terms_cuotes_range
        data['account_payment_terms_list'] = account_payment_terms_list
        return data
    
    @api.model
    def _process_order(self, order, draft, existing_order):
        _logger.warning('_process_order _____--______')
        _logger.warning(order)
        _logger.warning(draft)
        _logger.warning(existing_order)
        order_id = super(pos_order, self)._process_order(order, draft, existing_order)
        _logger.warning(order_id)
        try:
            if(int(order_id)>0):
                _order = self.env['pos.order'].sudo().browse(int(order_id))
                _order.sudo().update({
                                        'business_transaction_type': order.get('payment_terms_period') or 'without_credit',
                                     })
                self.update_statment_lines( _order )
        except:
            pass        
        return order_id
    
    def update_statment_lines( self, _pos_order ):
        statment_lines = _pos_order.get('statement_ids')
        _logger.warning('update_statment_lines')
        _logger.warning(statment_lines)
        if(statment_lines):
            for statment_line in statment_lines:
                try:
                    statment_line = statment_line[2]
                    account_statment_line = self.env['account.bank.statement.line'].sudo().browse(int(statment_line.get('statement_id')))

                    _logger.warning('account_statment_line')
                    _logger.warning(account_statment_line.id)
                    
                    account_statment_line.sudo().write({
                        'is_credit': bool(statment_line.get('is_credit')),
                        'fixed_period': bool(statment_line.get('fixed_period')),
                        'payment_terms_cuotes': int(statment_line.get('payment_terms_cuotes')),
                        'payment_terms_period': int(statment_line.get('payment_terms_period')),                    
                    })

                    _logger.warning('******************')
                    _logger.warning('account_statment_line.sudo().read()')
                    _logger.warning(account_statment_line.sudo().read())
                    _logger.warning('******************')

                except:
                    pass
            self.update_payment_terms(_pos_order)

    def update_payment_terms( self, _pos_order ):
        if( bool(_pos_order.get('is_credit')) ):
            if( bool(_pos_order.get('fixed_period')) ):
                _logger.warning("update_payment_terms: build_static_terms")
                static_terms = self.build_static_terms(_pos_order)
                _logger.warning(static_terms)
            else:
                self.build_dynamic_terms(_pos_order)
            pass
    
    def build_static_terms(self, _pos_order):
        payment_terms = _pos_order.get('payment_terms')
        _coutes = _pos_order.get('payment_terms_cuotes')
        _period = _pos_order.get('payment_terms_period')
        _period = self.env['account.payment.term'].sudo().browse(int(_period))
        _days = 0
        
        if(_period.line_ids):
                for _line in _period.line_ids:
                    _days = _line.days
                    break
        
        today = datetime.now().strftime("%m/%d/%y")
        if(_days>0):
            _date = datetime.strptime(today, "%m/%d/%y")
            _coute = 1
            
            while _coute <= _coutes:
                _next_date = _date + timedelta( days = (_days * _coute) )
                _next_date = dateutil.parser.parse(str(_next_date)).date()
                _item = {
                            'name':str('Cuota') + str(_coute).zfill(3), 
                            'date_due':_next_date,
                            'amount': round(float(amount_total / _coutes),2)
                        }                    
                payment_terms_period_dates.append(_item)
                _coute = int(_coute) + int(1)

    def action_pos_order_invoice(self):
        response = super(pos_order, self).action_pos_order_invoice()
        _logger.warning('action_pos_order_invoice - response')
        _logger.warning(response)

        if('res_id' in response):
            invoice_id = response['res_id']
            invoice = self.env['account.move'].sudo().browse(int(invoice_id))
            _logger.warning('invoice.read()')
            _logger.warning(invoice.read())

        return response

    def build_dynamic_terms(self, _pos_order):
        pass