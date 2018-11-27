from odoo import models, fields, api


class AccountMoveTemplate(models.Model):
    _name = 'account.move.template'
    _inherit = ['account.document.template',
                'mail.activity.mixin',
                'mail.thread']

    @api.model
    def _company_get(self):
        return self.env['res.company']._company_default_get(
            object='account.move.template'
        )

    company_id = fields.Many2one(
        'res.company',
        required=True,
        change_default=True,
        default=_company_get,
    )
    template_line_ids = fields.One2many(
        'account.move.template.line',
        inverse_name='template_id',
    )
    partner_id = fields.Many2one(
        'res.partner', string='Partner'
    )
    move_ids = fields.One2many(
        'account.move',
        inverse_name='template_id',
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('running', 'In Process'), ('done', 'Done')],
        string='Status', default='draft', required=True,
        readonly=True, copy=False
    )
    date_start = fields.Date(
        'Start Date', required=True, default=fields.Date.context_today)
    period_total = fields.Integer(
        'Number of Periods', required=True, default=12)
    period_nbr = fields.Integer('Period', required=True, default=1)
    period_type = fields.Selection(
        [('day', 'Days'), ('month', 'Months'), ('year', 'Years')],
        'Period Type', required=True, default='month')

    @api.multi
    def button_compute(self):
        self.ensure_one()
        action = self.env.ref(
            'account_move_template.action_wizard_select_template').read()[0]
        action.update({'context': {
            'default_template_id': self.id,
            'default_compute_moves': True,
        }})
        return action

    @api.multi
    def set_draft(self):
        for tmplt in self:
            tmplt.write({'state': 'draft'})
        return False

    @api.multi
    def remove_moves(self):
        for tmplt in self:
            tmplt.move_ids.filtered(
                lambda move: move.state == 'draft').unlink()
            tmplt.write({'state': 'draft'})
        return False

    @api.multi
    def action_run_template(self):
        self.ensure_one()
        action = self.env.ref(
            'account_move_template.action_wizard_select_template').read()[0]
        action.update({'context': {'default_template_id': self.id}})
        return action


class AccountMoveTemplateLine(models.Model):
    _name = 'account.move.template.line'
    _inherit = 'account.document.template.line'

    journal_id = fields.Many2one('account.journal', required=True)
    account_id = fields.Many2one(
        'account.account',
        required=True,
        ondelete="cascade"
    )
    move_line_type = fields.Selection(
        [('cr', 'Credit'), ('dr', 'Debit')],
        required=True
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        ondelete="cascade"
    )
    template_id = fields.Many2one('account.move.template')

    _sql_constraints = [
        ('sequence_template_uniq', 'unique (template_id,sequence)',
         'The sequence of the line must be unique per template !')
    ]


class AccountMove(models.Model):
    _inherit = 'account.move'

    template_id = fields.Many2one('account.move.template')
