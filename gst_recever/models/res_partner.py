# -*- coding: utf-8 -*-
# Copyright 2019 Guadaltech Soluciones Tecnológicos S.L (<http://guadaltech.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import *

class Partner(models.Model):
    _inherit = "res.partner"

    qr_recever_code = fields.Char(string="Recever QR", store=True)