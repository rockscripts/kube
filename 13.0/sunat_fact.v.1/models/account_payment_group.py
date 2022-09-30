
from odoo import models, fields, api, tools, _
import logging
_logger = logging.getLogger(__name__)

class account_payment_group(models.Model):

    _inherit = "account.payment.group"

    document_number = fields.Char(default="-")