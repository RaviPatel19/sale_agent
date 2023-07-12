from odoo import models, api, fields


class ResConfigSetting(models.TransientModel):
    _inherit='res.config.settings'

    commission_product_id = fields.Many2one(
            related='company_id.commission_product_id', readonly=False)
