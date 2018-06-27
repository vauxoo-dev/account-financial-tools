{
    'name': "Account Move Template",
    'version': '11.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'summary': "Templates for recurring Journal Entries",
    'author': "Agile Business Group,Odoo Community Association (OCA), Aurium "
              "Technologies,Vauxoo",
    'website': 'https://github.com/OCA/account-financial-tools',
    'license': 'AGPL-3',
    'depends': ['account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'view/move_template.xml',
        'wizard/select_template.xml',
        'wizard/validate_template.xml',
    ],
    'test': [
    ],
    'installable': True,
}
