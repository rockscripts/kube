# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class sunat_catalog(models.Model):
    _name = 'sunat.catalog'
    _description = 'información de catalogos para comprobantes electrónicos'

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one("res.company", "Company")
    code = fields.Char("Code", required=True)
    un_ece_code = fields.Char("UN/ECE Code")
    table_code = fields.Char("Table Code", required=True)
    state = fields.Boolean("Active", default=True)
    description = fields.Text("Description")
    value = fields.Float('Value', digits=(12, 6))
    un_ece_code_5305 = fields.Char("UN/ECE Code 5305")
    
    _sql_constraints = [ ('table_code_uniq', 'unique(code, table_code)', 'The code of the table must be unique by table code !') ]
    
    @api.model
    def build_selection(self, catalog):
        items = []
        datas = self.search([('table_code', '=', catalog)])
        if datas:
            items = [(data.code,data.name) for data in datas]
        return items

    @api.model
    def get_name_by_table(self, table_code, item_code):
        return self.search([('table_code', '=', table_code), ('code', '=', item_code)])

    @api.model
    def get_name_by_code(self, item_code):
        return self.search([('table_code', '=', 'PE.DOC.TYPE'), ('code', '=', item_code)])
    
    def get_payment(self, invoice):
        _type = invoice.sunat_payment_type
        _method = self.get_name_by_table('CATALOG59', invoice.sunat_payment_method)
        return {
                    'type':_type,
                    'code':_method.code,
                    'name':_method.name,
                }