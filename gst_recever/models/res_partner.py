# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import *

class Partner(models.Model):
    _inherit = "res.partner"

    qr_recever_code = fields.Char(string="Recever QR", store=True)