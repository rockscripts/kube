from odoo import api, fields, models, _

class res_representants(models.Model):

    _name = "res.representants"
    id_company = fields.Text(name="id_company", string="ID Company", default='')
    doc_type = fields.Selection([('0','RUC'),('1','DNI'),('4','CARNET DE EXTRANJERIA'),('6','REG. UNICO DE CONTRIBUYENTES'),('7','PASAPORTE'),('A','CED. DIPLOMATICA DE IDENTIDAD'),('B','DOC.IDENT.PAIS.RESIDENCIA-NO.D'),('C','Tax Identification invoice_sequence_number_next - TIN – Doc Trib PP.NN'),('D','Identification invoice_sequence_number_next - IN – Doc Trib PP. JJ')], string='Tipo Documento', default='6')
    doc_invoice_sequence_number_next = fields.Text(name="doc_invoice_sequence_number_next", string="Número de Documento", default='')
    name = fields.Text(name="name", string="Nombre", default='')
    position = fields.Text(name="position", string="Cargo", default='')
    address = fields.Text(name="address", string="Address", default='')
    date_added = fields.Text(name="date_added", string="Fecha desde", default='')