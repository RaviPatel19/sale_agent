from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent_id = fields.Many2one('res.partner', string='Agent')
    commission_percentage = fields.Float("Commission %")
