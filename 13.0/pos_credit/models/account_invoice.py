# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from datetime import datetime, timedelta
import dateutil.parser
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    _inherit = 'account.move'

    business_transaction_type = fields.Selection(selection=[('without_credit','Débito')], string="Tipo de Transacción" , default='without_credit')