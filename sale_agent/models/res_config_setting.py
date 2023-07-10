from odoo import models, api, fields


class ResConfigSetting(models.TransientModel):
     _inherit='res.config.settings'

     product_id = fields.Many2one(
          related='company_id.product_id', readonly=False, string='Default Product')
