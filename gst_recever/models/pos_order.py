from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    qr_recever_code = fields.Char(string="Recever/iRecever QR", store=True)


