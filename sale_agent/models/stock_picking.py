from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    consumer_note = fields.Html(compute='_compute_consumer_note')

    def _compute_consumer_note(self):
        for picking in self:
            picking.consumer_note = picking.sale_id.consumer_note