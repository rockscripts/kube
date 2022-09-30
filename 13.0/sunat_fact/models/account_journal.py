from odoo import models, fields, api, tools, _

class account_journal(models.Model):
    _inherit = 'account.journal'

    is_electronic_invoice = fields.Boolean(string="Facturación electronica")