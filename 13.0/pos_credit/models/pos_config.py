# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_config(models.Model):
    _inherit = 'pos.config'

    # tab .gob credit
    payment_terms_cuotes_range = fields.Integer( string="Rango Cuotas 1-X" , default=10)