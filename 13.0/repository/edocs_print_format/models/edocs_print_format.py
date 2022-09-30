from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.osv import osv

class edocs_print_format(models.Model):
    _inherit = 'ir.cron'