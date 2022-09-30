# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from sunatservice.sunatservice import Service
import json
import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceDebit(models.TransientModel):
    """Credit Notes"""

    _inherit = "account.debit.note"
    _description = "Notas de Debito"

    sunat_note = fields.Selection([('08','Débito')], string='Nota', default='08')
    DB_VALUES = [('01','Intereses de mora'),('02','Aumento en el valor'),('03','Penalidades / otros conceptos')]
    debit_discrepance = fields.Selection(DB_VALUES, string='Discrepancia', default='01')
    journal_id = fields.Many2one('account.journal', string='Diario Débito', help='If empty, uses the journal of the journal entry to be debited.',  default=lambda self: self._default_journal())
    copy_lines = fields.Boolean("Copiar Lineas Facturables",default=True, help="In case you need to do corrections for every line, it can be in handy to copy them.  We won't copy them for debit notes from credit notes. ")

    def _get_sunat_payment_method(self):
        return self.env['sunat.catalog'].build_selection("CATALOG59")
    sunat_payment_method = fields.Selection(selection="_get_sunat_payment_method", string="Medio de pago", default="004")
    sunat_payment_type = fields.Selection(selection=[('debit','Débito'), ('credit','Crédito')], string="Tipo de pago", default="debit")


    def _default_journal(self):
        account_journal = self.env['account.journal'].search([('code','=','NDB')], limit=1)
        #raise Warning(account_journal)
        if(account_journal):
            return account_journal.id
        else:
            raise Warning('Crear diario para nota débito electronica con codigo corto NDB.')

    @api.onchange('debit_discrepance')
    def onchange_debit_discrepance(self):
        self.reason = self.debit_discrepance
    
    def _prepare_default_values(self, move):
        if move.type in ('in_refund', 'out_refund'):
            type = 'in_invoice' if move.type == 'in_refund' else 'out_invoice'
        else:
            type = move.type
        
        discrepance_text = ''
        for selection in self.DB_VALUES:
            if(self.debit_discrepance == selection[0]):
                discrepance_text = selection[1]

        default_values = {
                                'ref': '%s, %s' % (move.name, self.reason) if self.reason else move.name,
                                'date': self.date or move.date,
                                'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                                'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
                                'invoice_payment_term_id': None,
                                'debit_origin_id': move.id,
                                'type': type,
                                'api_message':'Documento contable sin emitir.',
                                "discrepance_code":str(self.debit_discrepance),
                                "discrepance_text":str(discrepance_text),
                                'sunat_payment_method': move.sunat_payment_method,
                                'sunat_payment_type': move.sunat_payment_type,
                            }
        if not self.copy_lines or move.type in [('in_refund', 'out_refund')]:
            default_values['line_ids'] = [(5, 0, 0)]
        return default_values


class AccountInvoiceCredit(models.TransientModel):
    """Credit Notes"""

    _inherit = "account.move.reversal"
    _description = "Notas de Credito"
    journal_id = fields.Many2one('account.journal', string='Diario Crédito', help='If empty, uses the journal of the journal entry to be reversed.', default=lambda self: self._default_journal())

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.move'].browse(active_id)
            return inv.name
        return ''

    invoice_date = fields.Date(string='Fecha de la nota', default=fields.Date.context_today, required=True)
    date = fields.Date(string='Fecha Contable')
    description = fields.Char(string='Motivo', required=True, default=_get_reason)
    refund_only = fields.Boolean(string='Technical field to hide filter_refund in case invoice is partially paid', compute='_get_refund_only')
    filter_refund = fields.Selection([('refund', 'Create a draft credit note'), ('cancel', 'Cancel: create credit note and reconcile'), ('modify', 'Modify: create credit note, reconcile and create a new draft invoice')],
    #filter_refund = fields.Selection([('refund', 'Crear nota para validar')],
        default='refund', string='Method', required=True, help='Elige cómo quieres acreditar o debitar esta factura. No puede modificar y cancelar si la factura ya está conciliada')
    sunat_note = fields.Selection([('07','Crédito')], string='Nota', default='07')
    CD_VALUES = [('01','Anulación operación'),('02','Anulacion error RUC'),('03','Corrección en descripción'),('04','Descuento global'),('05','Descuento por Item'),('06','Descuento Total'),('07','Devolución por Item'),('08','Bonificación'),('09','Disminución en valor'),('10','Otros conceptos')]
    credit_discrepance = fields.Selection(CD_VALUES, string='Discrepancia', default='01')
    DB_VALUES = [('01','Intereses de mora'),('02','Aumento en el valor'),('03','Penalidades / otros conceptos')]
    debit_discrepance = fields.Selection(DB_VALUES, string='Discrepancia', default='01')

    def _get_sunat_payment_method(self):
        return self.env['sunat.catalog'].build_selection("CATALOG59")
    sunat_payment_method = fields.Selection(selection="_get_sunat_payment_method", string="Medio de pago", default="004")
    sunat_payment_type = fields.Selection(selection=[('debit','Débito'), ('credit','Crédito')], string="Tipo de pago", default="debit")



    def _default_journal(self):
        account_journal = self.env['account.journal'].search([('code','=','NCR')], limit=1)
        if(account_journal):
            return  account_journal.id
        else:
            raise Warning('Crear diario para nota débito electronica con codigo corto NCR.')
    
    @api.onchange('credit_discrepance')
    def onchange_debit_discrepance(self):
        self.reason = self.credit_discrepance

    
            
    @api.depends('invoice_date')
    
    def _get_refund_only(self):
        self.ensure_one()
        invoice_id = self.env['account.move'].browse(self._context.get('active_id',False))
        #raise Warning(invoice_id.read())
        if (len(invoice_id.line_ids) != 0 and invoice_id.state != 'paid'):
            self.refund_only = True
        else:
            self.refund_only = False

    def reverse_moves(self):
        journal_obj = self.env['account.journal']

        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        _logger.warning("self.refund_method")       
        _logger.warning(self.refund_method)   
        _logger.warning(self.sunat_note)

        # Handle reverse method.
        if self.refund_method == 'cancel':
            if(self.sunat_note=="07"):   
                _logger.warning("MOVED")          
                new_moves = moves._reverse_moves(default_values_list)
            else:
                if any([vals.get('auto_post', True) for vals in default_values_list]):
                    new_moves = moves._reverse_moves(default_values_list)
                else:
                    new_moves = moves._reverse_moves(default_values_list, cancel=True)
        elif self.refund_method == 'modify':
            moves._reverse_moves(default_values_list, cancel=True)
            moves_vals_list = []
            for move in moves.with_context(include_business_fields=True):
                moves_vals_list.append(move.copy_data({
                    'date': self.date or move.date,
                })[0])
            new_moves = self.env['account.move'].create(moves_vals_list)
        elif self.refund_method == 'refund':            
            new_moves = moves._reverse_moves(default_values_list)
        else:
            return

        invoiceNote = self.env['account.move'].browse(int(new_moves.id))

        action_name = _('Reverse Moves')

        if(self.sunat_note=="07"):
            journal = journal_obj.search([('code','=',str("NCR"))])
            discrepance_text = ''
            for selection in self.CD_VALUES:
                if(self.credit_discrepance == selection[0]):
                    discrepance_text = selection[1]
                
            invoiceNote.update({'api_message':'Documento contable sin emitir.', "journal_id":int(journal.id),"discrepance_code":str(self.credit_discrepance),"discrepance_text":str(discrepance_text),"type":"out_refund"})
          
        if(self.sunat_note=="08"):
            action_name = 'Notas de Débito'
            journal = journal_obj.search([('code','=',str("NDB"))])
            discrepance_text = ''
            for selection in self.DB_VALUES:
                if(self.debit_discrepance == selection[0]):
                    discrepance_text = selection[1]
            invoiceNote.update({'api_message':'Documento contable sin emitir.',"journal_id":int(journal.id),"discrepance_code":str(self.debit_discrepance),"discrepance_text":str(discrepance_text),"type":"out_invoice"})
           
            invoiceNote.update({
                                'amount_untaxed_signed':str(float(float(invoiceNote.amount_untaxed_signed)*float(-1.0))),
                                'amount_tax_signed':str(float(float(invoiceNote.amount_tax_signed)*float(-1.0))),
                                'amount_total_signed':str(float(float(invoiceNote.amount_total_signed)*float(-1.0))),
                                'amount_residual_signed':str(float(float(invoiceNote.amount_residual_signed)*float(-1.0))),
                                })
                                
        invoice_domain = [('id', 'in', new_moves.ids)]
        if(self.sunat_note=="08"):
            invoice_domain.append(('type', '=', 'out_invoice'))

        # Create action.
        action = {
            'name': action_name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(new_moves) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': new_moves.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': invoice_domain,
            })
        return action



#*****CLASS NOT USED
class AccountInvoiceRefund(models.TransientModel):
    """Credit Notes"""

    _name = "account.move.refund"
    _description = "Notas Sin Uso"