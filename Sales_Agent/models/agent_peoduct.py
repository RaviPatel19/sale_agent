from odoo import fields,models

class AgentProduct(models.Model):
     _inherit = 'res.company'


     agent_commision_product_id = fields.Many2one('product.product', string='Default Product')
