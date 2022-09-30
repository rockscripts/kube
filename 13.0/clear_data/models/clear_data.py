# -*- coding: utf-8 -*-

'''
Create Date:2017��9��1��

Author     :Administrator
'''
import datetime
import dateutil
import logging
import os
import time
import pdb
import logging
import odoo.tools
_logger = logging.getLogger(__name__)

from pytz import timezone

import odoo
from odoo import api, fields, models, tools, _
from odoo.exceptions import MissingError, UserError, ValidationError

class ClearDataModel(models.Model):
    _name='clear.data.model'
    
    name=fields.Char(string="Model group")