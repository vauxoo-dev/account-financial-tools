# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID, api, fields


def create_journal_sequences(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        journals = env["account.journal"].with_context(active_test=False).search([])
        # _get_last_sequence
        # _compute_split_sequence
        # TODO: Set the date in the context calling the sequence because it is range_date and it is using January
        for journal in journals:
            # TODO: Get the last refund move based on journal.refund_sequence == True
            # if self.journal_id.refund_sequence:
            #     if self.move_type in ('out_refund', 'in_refund'):
            #         where_string += " AND move_type IN ('out_refund', 'in_refund') "
            #     else:
            #         where_string += " AND move_type NOT IN ('out_refund', 'in_refund') "

            last_move = env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('posted_before', '=', True),
                # ('move_type', 'not =like', '%\_refund'),
            ], limit=1, order='id DESC')
            # TODO: Get last sequence when there are not last_move related
            seq_extra_vals = {}
            if last_move:
                last_sequence = last_move._get_last_sequence()
                if not last_sequence:
                    last_sequence = last_move._get_last_sequence(relaxed=True) or last_move._get_starting_sequence()

                seq_format, seq_format_values = last_move._get_sequence_format_param(last_sequence)
                prefix1 = seq_format_values['prefix1']
                prefix = prefix1
                # where = "WHERE name LIKE '%s%%'" % prefix
                # where_name_value += 
                if seq_format_values['year_length'] == 4:
                    prefix += '%(range_year)s'
                elif seq_format_values['year_length'] == 2:
                    prefix += '%(range_y)s'
                prefix2 = seq_format_values.get('prefix2') or ""
                prefix += prefix2
                month = seq_format_values.get('month')  # It is 0 if only have year
                if month:
                    prefix += '%(range_month)s'
                    # TODO: Create date range ids based on the month but avoid duplicating
                    # TODO: Avoid duplicating sequence if it is shared
                prefix3 = seq_format_values.get('prefix3') or ""
                where_name_value = "%s%s%s%s%s%%" % (prefix1, '_' * seq_format_values['year_length'], prefix2, '_' * bool(month)*2, prefix3)
                select_name_values = []
                prefixes = prefix1
                if prefix2:
                    prefixes += prefix2
                    select_name_values.append("split_part(name, '%s', %d)" % (prefix2, prefixes.count(prefix2)))
                if prefix3:
                    prefixes += prefix3
                    select_name_values.append("split_part(name, '%s', %d)" % (prefix3, prefixes.count(prefix3)))
                select_max_value = "MAX(split_part(name, '%s', %d)::INTEGER) AS max_number" % (prefixes[-1], prefixes.count(prefixes[-1]) + 1)
                query = "SELECT %s, %s FROM account_move WHERE name LIKE '%s' AND journal_id=%d GROUP BY %s" % (', '.join(select_name_values), select_max_value, where_name_value, journal.id, ', '.join(select_name_values))
                env.cr.execute(query)
                res = env.cr.fetchall()
                date_range_lines = []
                for year, month, max_number in res:
                    # TODO: Check <=1999 year but 2 digits
                    # TODO: Consider date 01
                    # TODO: if month is not present so only create year range
                    date_from = fields.Date.to_date('%s-%s-1' % (year, month))
                    date_to = date_from + relativedelta(day=31)
                    date_range_lines.append((0, 0, {
                        'date_from': date_from,
                        'date_to': date_to,
                        'number_next_actual': max_number + 1,
                    }))
                # print(date_range_lines)
                # for i in 
                
                prefix += prefix3
                seq_extra_vals = {
                    'padding': seq_format_values['seq_length'],
                    'suffix': seq_format_values['suffix'],
                    'prefix': prefix,
                    'date_range_ids': date_range_lines,
                }

            vals = {}
            journal_vals = {
                "code": journal.code,
                "name": journal.name,
                "company_id": journal.company_id.id,
            }
            seq_vals = journal._prepare_sequence(journal_vals)
            seq_vals.update(seq_extra_vals)
            vals["sequence_id"] = env["ir.sequence"].create(seq_vals).id
            if journal.type in ("sale", "purchase") and journal.refund_sequence:
                rseq_vals = journal._prepare_sequence(journal_vals, refund=True)
                vals["refund_sequence_id"] = env["ir.sequence"].create(rseq_vals).id
            journal.write(vals)
    return
