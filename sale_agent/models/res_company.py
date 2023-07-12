from odoo import fields,models


class ResCompany(models.Model):
     _inherit = 'res.company'

     commission_product_id = fields.Many2one('product.product', string='Default Product')
