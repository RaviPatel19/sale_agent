{
    'name':'Sales Agent',
    'summary':'Sales Agent Commision',
    'devloper':'Ravi',
    'depends': ['base', 'sale'],
    'license': 'LGPL-3',
    'data':['security/ir.model.access.csv',
            'views/res_partner.xml',
            'views/sale_order_template.xml',
            # 'views/sales_order_template.xml',
            'views/sale_order.xml',
            'views/product_res_config.xml'
            ]

}