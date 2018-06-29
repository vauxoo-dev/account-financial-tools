from odoo import models, fields


class WizardValidateMoveTemplate(models.TransientModel):

    _name = "wizard.validate.move.template"
    date = fields.Date(
        'Validate Recurring Entries Before', required=True,
        default=fields.Date.context_today)

    def action_validate_moves(self):
        templates = self.env['account.move.template'].search(
            [('state', '=', 'running')])
        moves_ids = []
        for template in templates:
            for move in template.move_ids.filtered(
                    lambda mov: mov.state == 'draft' and mov.date < self.date):
                move.post()
                moves_ids.append(move.id)
            draft_moves = template.move_ids.filtered(
                lambda mov: mov.state == 'draft')
            if not draft_moves:
                template.write({'state': 'done'})
        return {
            'domain': [('id', 'in', moves_ids)],
            'name': 'Validated Recurring Entries bdefore: %s' % self.date,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
