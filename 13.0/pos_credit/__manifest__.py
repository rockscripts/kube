# -*- coding: utf-8 -*-
{
    'name': "Credit Orders",

    'summary': """
        Credit Orders
    """,

    'description': """
        Credit Orders
    """,

    'author': "rockscripts",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [ 
                    'base', 
                    'point_of_sale', 
                    'web', 
                    'bus', 
                    'account',                     
                    'sale' 
                ],
    'data': [   
                'views/pos_config.xml',
                'views/pos_order.xml',
                'views/payment_terms.xml',
                'views/account_journal.xml',
                'views/account_invoice.xml',
                'views/account_bank_statment_line.xml',
                'views/views.xml',
                'views/templates.xml',
                'views/menu.xml',
                #'security/payment.terms.csv',
                
            ],
    'qweb': [
                'static/src/xml/PaymentScreen/PaymentScreenPaymentLines.xml',
                'static/src/xml/Popup/PopupCreditTerms.xml',
            ],
}