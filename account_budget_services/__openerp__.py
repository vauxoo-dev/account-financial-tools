# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ########### Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


{
    "name": "Account Budget Services",
    "version": "1.0",
    "category": "Account",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com",
    "depends": [
        "base",
        "account_budget",
        "report_webkit",
    ],
    "data": [
        "data/budget_css.xml",
        "report/budget_report.xml",
        "view/account_budget_view.xml",
    ],
    "test": [],
    "images": [],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
