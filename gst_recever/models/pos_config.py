from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'
    _description = ''


    street = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    ticket_message = fields.Text()


