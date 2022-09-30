# -*- coding: utf-8 -*-
{
    'name': 'F.E - Sunat - PDF Formatos impresión',
    'description': "Addon para mejorar plantillas pdf de reportes con F.E",
    'author': "ROCKSCRIPTS",
    'website': "https://instagram.com/rockscripts",
    'summary': "Formato para documentos contables",
    'version': '0.1',
    "license": "OPL-1",
    'price':'40',
    'currency':'USD',
    'support': 'rockscripts@gmail.com',
    'category': 'module_category_account_voucher',
    "images": ["images/banner.png"],
    'depends': ['base','account'],
    'data': [
             'views/templates.xml',
             'views/template_invoice.xml',
             'views/report_deliveryslip.xml',
            ],
    'installable': True,
}
