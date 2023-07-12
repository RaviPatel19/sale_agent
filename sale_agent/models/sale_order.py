from odoo import models, api, fields, Command
from datetime import date
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agent_id = fields.Many2one('res.partner', 
            string="Agent", 
            compute='_compute_agent_id',
            store=True, readonly=False)
    commission = fields.Float(compute='_compute_commission', string='Commission %', readonly=False, store=True)
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
            compute='_compute_amount_paid_agent', 
            string='Amount Paid To Agent')
    pcercentage_of_commission_paid_to_agent = fields.Float(compute='_compute_paid_agent_commission_percentge',string='Percentage Of Commison Paid To Agent')

    def _compute_amount_paid_agent(self):
        for order_id in self:
            order_id.amount_paid_agent = sum(order_id.agent_invoice_ids.filtered(lambda x: x.payment_state == 'paid').mapped('amount_total'))

    @api.depends('partner_id')
    def _compute_agent_id(self):
        for order_id in self:
            order_id.agent_id = order_id.partner_id.agent_id

    @api.depends('partner_id')
    def _compute_commission(self):
        for order_id in self:
            commission_percentage = order_id.partner_id.commission_percentage
            self.commission = commission_percentage * 100

    @api.depends('amount_untaxed', 'commission')
    def _compute_commission_amount(self):
        for order_id in self:
            commission = (order_id.amount_untaxed * order_id.commission) / 100
            order_id.commission_amount = commission

    def create_agent_bill(self):
        self.ensure_one()
        if not self.company_id.commission_product_id:
            raise UserError("Configure agent product in config.")
        if self.commission_amount > 0:
            invoice_id = self.env['account.move'].create({
                'partner_id': self.agent_id.id,
                'sale_order_id': self.id,
                'currency_id': self.currency_id.id,
                'move_type':'out_invoice',
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_line_ids': [
                    Command.create({
                        'product_id': self.company_id.commission_product_id.id,
                        'price_unit': self.commission_amount
                    })
                ]
            })
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_in_invoice_type')
            action['res_id'] = invoice_id.id
            action['views'] = [(False, 'form')]
            return action

    def _compute_get_agent_invoiced_count(self):
        for order_id in self:
            order_id.invoice_count = len(order_id.agent_invoice_ids)

    def action_view_state(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.agent_invoice_ids.ids)]
        action['views'] = [(False, 'list'), (False, 'form')]
        return action

    @api.depends('invoice_ids.state')
    def _compute_agent_bill_state(self):
            self.agent_bill_state = 'draft'

    def _compute_paid_agent_commission_percentge(self):
        for order_id in self:
            total_bill_amount = sum(order_id.agent_invoice_ids.filtered(lambda x: x.payment_state not in ['cancel']).mapped('amount_total'))
            if total_bill_amount:
                order_id.pcercentage_of_commission_paid_to_agent = order_id.amount_paid_agent / total_bill_amount
            else:
                order_id.pcercentage_of_commission_paid_to_agent = 0
