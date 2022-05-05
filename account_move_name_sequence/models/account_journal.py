# Copyright 2021 Akretion France (http://www.akretion.com/)
# Copyright 2022 Vauxoo (https://www.vauxoo.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# @author: Moisés López <moylop260@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    sequence_id = fields.Many2one(
        "ir.sequence",
        string="Entry Sequence",
        copy=False,
        check_company=True,
        domain="[('company_id', '=', company_id)]",
        help="This sequence will be used to generate the journal entry number.",
    )
    refund_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Credit Note Entry Sequence",
        copy=False,
        check_company=True,
        domain="[('company_id', '=', company_id)]",
        help="This sequence will be used to generate the journal entry number for refunds.",
    )

    @api.constrains("refund_sequence_id", "sequence_id")
    def _check_journal_sequence(self):
        for journal in self:
            if (
                self.refund_sequence_id
                and self.sequence_id
                and self.refund_sequence_id == self.sequence_id
            ):
                raise ValidationError(
                    _(
                        "On journal '%s', the same sequence is used as "
                        "Entry Sequence and Credit Note Entry Sequence."
                    )
                    % self.display_name
                )
            if self.sequence_id and not self.sequence_id.company_id:
                raise ValidationError(
                    _(
                        "The company is not set on sequence '%s' configured on "
                        "journal '%s'."
                    )
                    % (self.sequence_id.display_name, self.display_name)
                )
            if self.refund_sequence_id and not self.refund_sequence_id.company_id:
                raise ValidationError(
                    _(
                        "The company is not set on sequence '%s' configured as "
                        "credit note sequence of journal '%s'."
                    )
                    % (self.refund_sequence_id.display_name, self.display_name)
                )

    @api.model
    def create(self, vals):
        if not vals.get("sequence_id"):
            vals["sequence_id"] = self._create_sequence(vals).id
        if (
            vals.get("type") in ("sale", "purchase")
            and vals.get("refund_sequence")
            and not vals.get("refund_sequence_id")
        ):
            vals["refund_sequence_id"] = self._create_sequence(vals, refund=True).id
        return super().create(vals)

    
    def _prepare_sequence_current_moves(self, refund=False):
        """Get sequence dict values the journal based on current moves"""
        self.ensure_one()
        move_domain = [
            ('journal_id', '=', self.id),
            ('posted_before', '=', True),
        ]
        if self.refund_sequence:
            # Based on original Odoo behavior
            if refund:
                move_domain.append(('move_type', 'NOT IN', ('out_refund', 'in_refund')))
            else:
                move_domain.append(('move_type', 'IN', ('out_refund', 'in_refund')))
        last_move = self.env['account.move'].search(move_domain, limit=1, order='id DESC')
        msg_err = "Journal %s could not get sequence %s values based on current moves. Using default values." % (self.id, refund and "refund" or "")
        if not last_move:
            _logger.warning("%s %s", msg_err, "No moves found")
            return {}
        try:
            # Big try-except because of get the current sequence values could be hard to get and buggy
            # But even we can use the default values or do manual changes instead of raising errors
            last_sequence = last_move._get_last_sequence()
            if not last_sequence:
                last_sequence = last_move._get_last_sequence(relaxed=True) or last_move._get_starting_sequence()

            __, seq_format_values = last_move._get_sequence_format_param(last_sequence)
            prefix1 = seq_format_values['prefix1']
            prefix = prefix1
            if seq_format_values['year_length'] == 4:
                prefix += '%(range_year)s'
            elif seq_format_values['year_length'] == 2:
                prefix += '%(range_y)s'
            prefix2 = seq_format_values.get('prefix2') or ""
            prefix += prefix2
            month = seq_format_values.get('month')  # It is 0 if only have year
            if month:
                prefix += '%(range_month)s'
            prefix3 = seq_format_values.get('prefix3') or ""
            where_name_value = "%s%s%s%s%s%%" % (prefix1, '_' * seq_format_values['year_length'], prefix2, '_' * bool(month)*2, prefix3)
            select_name_values = []
            prefixes = prefix1 + prefix2
            select_name_values.append("split_part(name, '%s', %d)" % (prefix2, prefixes.count(prefix2)) if prefix2 else "''")
            prefixes += prefix3
            select_name_values.append("split_part(name, '%s', %d)" % (prefix3, prefixes.count(prefix3)) if prefix3 else "''")
            select_max_value = "MAX(split_part(name, '%s', %d)::INTEGER) AS max_number" % (prefixes[-1], prefixes.count(prefixes[-1]) + 1)
            query = "SELECT %s, %s FROM account_move WHERE name LIKE '%s' AND journal_id=%d GROUP BY 1,2" % (', '.join(select_name_values), select_max_value, where_name_value, self.id)
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()
            prefix += prefix3
            seq_vals = {
                'padding': seq_format_values['seq_length'],
                'suffix': seq_format_values['suffix'],
                'prefix': prefix,
                'date_range_ids': [],
                'use_date_range': True,
            }
            for year, month, max_number in res:
                if not year and not month:
                    seq_vals.update({
                        'use_date_range': False,
                        'number_next_actual': max_number + 1,
                    })
                    continue
                if len(year) == 2:
                    # Year >=50 will be considered as last century 1950
                    # Year <=49 will be considered as current century 2049
                    if int(year) >= 50:
                        year = '19' + year
                    else:
                        year = '20' + year
                if month:
                    date_from = fields.Date.to_date('%s-%s-1' % (year, month))
                    date_to = date_from + relativedelta(day=31)
                else:
                    date_from = fields.Date.to_date('%s-1-1' % year)
                    date_to = fields.Date.to_date('%s-12-31' % year)
                seq_vals['date_range_ids'].append((0, 0, {
                    'date_from': date_from,
                    'date_to': date_to,
                    'number_next_actual': max_number + 1,
                }))
            return seq_vals
        except Exception as e:
            _logger.warning("%s %s", msg_err, e)
        return {}

    @api.model
    def _prepare_sequence(self, vals, refund=False):
        code = self.code.upper() or ""
        prefix = "%s%s/%%(range_year)s/%%(range_month)s/" % (refund and "R" or "", code)
        seq_vals = {
            "name": "%s%s" % (self.name or _("Sequence"), refund and _("Refund") + " " or ""),
            "company_id": self.company_id.id or self.env.company.id,
            "implementation": "no_gap",
            "prefix": prefix,
            "padding": 4,
            "use_date_range": True,
        }
        return seq_vals

    @api.model
    def _create_sequence(self, vals, refund=False):
        seq_vals = self._prepare_sequence(vals, refund=refund)
        return self.env["ir.sequence"].sudo().create(seq_vals)
