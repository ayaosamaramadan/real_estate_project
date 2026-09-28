# -*- coding: utf-8 -*-
{
    'name': "real_estate",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'crm', 'portal', 'website'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'wizard/mani.xml',
        'wizard/lease_wizard.xml',
        'wizard/tenant_wizard.xml',
        'wizard/rent_roll_wizard_views.xml',
        'wizard/main_report_wizard.xml',
        'report/prop_report_temp.xml',
        'report/report.xml',
        'report/lease_report_temp.xml',
        'views/views.xml',
        'views/web_templates.xml',
        'views/property_views.xml',
        'views/tenant_views.xml',
        'views/lease_views.xml',
        'views/maintenance.xml',
        'views/res_par.xml',
        'views/crm_lead.xml',
        'views/payment_views.xml',
        'views/portal_templates.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

