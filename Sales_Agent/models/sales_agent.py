from odoo import models, api, fields


class SalesAgent(models.Model):
     _inherit = 'res.partner'

     agent_name = fields.Many2one('res.partner', string='Agent')
     commision_percentage = fields.Float("Commision",default=0)
