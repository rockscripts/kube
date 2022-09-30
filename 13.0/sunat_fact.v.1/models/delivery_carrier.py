from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.osv import osv

class delivery_carrier(models.Model):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"

    ruc = fields.Char('RUC', translate=True)
    placa = fields.Char('Placa', translate=False)