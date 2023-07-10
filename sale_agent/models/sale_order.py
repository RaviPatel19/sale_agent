from odoo import models, api, fields, Command
from datetime import date
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agent_id = fields.Many2one('res.partner', 
            string="Agent Name", 
            compute='_compute_agent_name',
            store=True, readonly=False)
    commision = fields.Integer(compute='_compute_commission', string='Commission', readonly=False, store=True)
    commission_amount = fields.Monetary(compute='_compute_commission_amount',string='Commission Amount')
    invoice_count = fields.Integer(compute='_compute_get_agent_invoiced_count')
    agent_bill_state = fields.Selection([
            ('draft','Draft'),
            ('posted','Posted'),
            ('cancel','Cancel'),
            ('partial_paid', 'Partial Paid')], 
            string='Agent Bill State', 
            compute='_compute_agent_bill_state')
    agent_invoice_ids = fields.One2many('account.move', 'sale_order_id', string='Agent Bill')
    amount_paid_agent = fields.Float(
            compute='_compute_amount_paid_to_agent', 
            string='Amount Paid To Agent')
    pcercentage_of_commision_paid_to_agent = fields.Float(compute='_compute_paid_agent_commision_percentge',string='Percentage Of Commison Paid To Agent')

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
            agent.agent_id = agent.partner_id.agent_id

    @api.depends('partner_id')
    def _compute_commission(self):
            commission_percentage = self.partner_id.commission_percentage
            self.commision = commission_percentage*100

    @api.depends('amount_total', 'commision')
    def _compute_commission_amount(self):
            for order in self:
                commission=(order.amount_total*order.commision)/100
                order.commission_amount = commission

    def create_agent_bill(self):
        defaut_product = self.env['res.company'].browse(self.company_id.id)
        agent_product_id = defaut_product.product_id.id
        if self.order_line and self.commission_amount > 0:
            invoice = self.env['account.move'].create({
                'partner_id': self.agent_id.id,
                # 'invoice_date':date.today(),
                'sale_order_id': self.id,
                'currency_id': self.currency_id.id,
                'move_type':'out_invoice',
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_line_ids': [
                        Command.create({
                            'product_id': agent_product_id,
                            'price_unit': self.commission_amount
                        })]
            })
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_in_invoice_type')
            action['res_id'] = invoice.id
            action['views'] = [(False, 'form')]
            return action
        else:
            raise UserError('There Is No Product In Order Line Or Commision Amount Is Not Zero')

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

    def _compute_paid_agent_commision_percentge(self):
        agent_bill_record = self.agent_invoice_ids
        total_agent_bill_amount = 0
        percentage_of_commision_paid_to_agent = 0
        for agent_bill_amount in agent_bill_record:
            total_agent_bill_amount += agent_bill_amount.amount_total_signed
            if agent_bill_amount.state == 'posted':
                percentage_of_commision_paid_to_agent += agent_bill_amount.invoice_line_ids.price_total
        if total_agent_bill_amount:
            cal_percentage_of_agent_bill_paid = (percentage_of_commision_paid_to_agent)/total_agent_bill_amount
            self.pcercentage_of_commision_paid_to_agent = cal_percentage_of_agent_bill_paid
        else:
            self.pcercentage_of_commision_paid_to_agent = 0
