# -*- coding: utf-8 -*-
# Copyright 2019 Guadaltech Soluciones Tecnológicos S.L (<http://guadaltech.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models, _


class CustomReceverwizard(models.TransientModel):
    _name = "custom.recever.wizard"

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)
