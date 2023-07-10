{
    'name':'Sales Agent',
    'summary':'Sales Agent Commission',
    'devloper':'Ravi',
    'depends': ['base', 'sale'],
    'license': 'LGPL-3',
    'data':['security/ir.model.access.csv',
            'views/res_partner.xml',
            'views/sale_order_template.xml',
            # 'views/sales_order_template.xml',
            'views/sale_order.xml',
            'views/res_config_setting.xml'
            ]

}