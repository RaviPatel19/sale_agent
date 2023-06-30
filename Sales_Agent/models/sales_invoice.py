from odoo import models, api, fields, Command
from datetime import date
from odoo.exceptions import UserError


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
          if self.agent_name_id:
               defaut_product = self.env['res.company'].browse(self.company_id.id)
               agent_product_id = defaut_product.agent_commision_product_id.id
               invoice = self.env['account.move'].create({'partner_id': self.agent_name_id.id,
                                                            'invoice_date':date.today(),
                                                            'currency_id': self.currency_id.id,
                                                            'move_type':'out_invoice',
                                                            'invoice_payment_term_id': self.payment_term_id.id,
                                                            'invoice_line_ids': [Command.create({'product_id': agent_product_id, 'price_unit': self.commision_amount})]
                                                            })
               return{
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model':'account.move',
                    'target': 'new',
                    'res_id': invoice.id}
          raise UserError("Agent Bill Is Not Required")
          # print('---------------------------------------------------',invoice,
          #           invoice.partner_id.name, invoice.invoice_payment_term_id)
