{
    'name':'Sales Agent',
    'summary':'Sales Agent Commission',
    'author':'Ravi',
    'depends': ['sale'],
    'license': 'LGPL-3',
    'data':['security/ir.model.access.csv',
            'views/res_partner.xml',
            'views/sale_order_template.xml',
            # 'views/sales_order_template.xml',
            'views/sale_order.xml',
            'views/res_config_setting.xml',
            'views/stock_picking.xml',
            'views/report_stockpicking_opration.xml'
            ]
}