# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class account_journal(models.Model):
    _inherit = 'account.journal'

    for_credit = fields.Boolean( string="Fiado / Cŕedito" , default=False)
    
    @api.model
    def get_journal_payment(self, _id=None):
        _logger.warning('get_journal_payment id')
        _logger.warning(_id)
        if(_id):
            return self.env['account.journal'].sudo().browse(int(_id)).read()
        else:
            return None