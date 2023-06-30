from odoo import models, api, fields


class SalesInvoice(models.Model):
     _inherit = 'sale.order'

     agent_name_id = fields.Many2one('res.partner', string="Agent Name", compute='_compute_agent_name',
                              store=True, readonly=False)
     commision = fields.Integer(
          compute='_compute_commision', string='Commision', readonly=False, store=True)
     company_id = fields.Many2one(
          comodel_name='res.company',
          required=True, index=True,
          default=lambda self: self.env.company)
     commision_amount = fields.Monetary(compute='_compute_commision_amount',string='Commision Amount')

     @api.depends('partner_id')
     def _compute_agent_name(self):
          for agent in self:
               agent = agent.with_company(agent.company_id)
               agent.agent_name_id = agent.partner_id.agent_name

     @api.depends('partner_id')
     def _compute_commision(self):
          for commision in self:
               commision = commision.with_company(commision.company_id)
               commision.commision = commision.partner_id.commision_percentage

     @api.depends('amount_total', 'commision')
     def _compute_commision_amount(self):
          for order in self:
               commision=(order.amount_total*order.commision)/100
               order.commision_amount = commision

     def create_agent_bill(self):
          pass
