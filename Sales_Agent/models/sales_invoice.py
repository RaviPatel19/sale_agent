from odoo import models, api, fields, Command
from datetime import date
from odoo.exceptions import UserError

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}

class SalesInvoice(models.Model):
    _inherit = 'sale.order'

    agent_name_id = fields.Many2one('res.partner', 
            string="Agent Name", 
            compute='_compute_agent_name',
            store=True, readonly=False)
    commision = fields.Integer(compute='_compute_commision', string='Commision', readonly=False, store=True)
    company_id = fields.Many2one(
            comodel_name='res.company',
            required=True, index=True,
            default=lambda self: self.env.company)
    commision_amount = fields.Monetary(compute='_compute_commision_amount',string='Commision Amount')
    order_line = fields.One2many(
            comodel_name='sale.order.line',
            inverse_name='order_id',
            string="Order Lines",
            states=LOCKED_FIELD_STATES,
            copy=True, auto_join=True)
    invoice_ids = fields.Many2many(
            comodel_name='account.move',
            string="Invoices",
            compute='_compute_get_invoiced',
            copy=False)
    invoice_count = fields.Integer(compute='_compute_get_agent_invoiced_count')
    agent_bill_state = fields.Selection([
            ('draft','Draft'),
            ('posted','Posted'),
            ('cancel','Cancel'),
            ('partial_paid', 'Partial Paid')], 
            string='Agent Bill State', 
            compute='_compute_agent_bill_state')
    # invoice_ids = fields.One2many('account.move', 'sale_order_id',string='invoice')
    agent_invoice_ids = fields.One2many('account.move', 'sale_order_id', string='Agent Bill')
    amount_paid_agent = fields.Float(
            compute='_compute_amount_paid_to_agent', 
            string='Amount Paid To Agent')
    
    def _compute_amount_paid_to_agent(self):
        agent_bill_record = self.agent_invoice_ids
        bill_amount_paid_to_agent = 0
        for agent_bill in agent_bill_record:
            if agent_bill.state =='posted':
                bill_amount_paid_to_agent += agent_bill.invoice_line_ids.price_total
        self.amount_paid_agent = bill_amount_paid_to_agent

    @api.depends('partner_id')
    def _compute_agent_name(self):
        for agent in self:
            agent.agent_name_id = agent.partner_id.agent_name

    @api.depends('partner_id')
    def _compute_commision(self):
        for commision in self:
            commision.commision = commision.partner_id.commision_percentage

    @api.depends('amount_total', 'commision')
    def _compute_commision_amount(self):
            for order in self:
                commision=(order.amount_total*order.commision)/100
                order.commision_amount = commision

    def create_agent_bill(self):
        defaut_product = self.env['res.company'].browse(self.company_id.id)
        agent_product_id = defaut_product.agent_commision_product_id.id
        if self.order_line and self.commision_amount > 0:
            invoice = self.env['account.move'].create({
                'partner_id': self.agent_name_id.id,
                # 'invoice_date':date.today(),
                'sale_order_id': self.id,
                'currency_id': self.currency_id.id,
                'move_type':'out_invoice',
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_line_ids': [
                        Command.create({
                            'product_id': agent_product_id,
                            'price_unit': self.commision_amount
                        })]
            })
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_in_invoice_type')
            action['res_id'] = invoice.id
            action['views'] = [(False, 'form')]
            return action
        else:
            raise UserError('There Is No Product In Order Line Or Commision Amount Is Not Zero')

    def _compute_get_invoiced(self):
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(
            lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices

    def _compute_get_agent_invoiced_count(self):
        self.invoice_count = len(self.agent_invoice_ids)

    def action_view_state(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.agent_invoice_ids.ids)]
        action['views'] = [(False, 'list'), (False, 'form')]
        return action

    @api.depends('invoice_ids.state')
    def _compute_agent_bill_state(self):
            self.agent_bill_state = 'draft'


class SaleId(models.Model):
    _inherit='account.move'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order Id')

