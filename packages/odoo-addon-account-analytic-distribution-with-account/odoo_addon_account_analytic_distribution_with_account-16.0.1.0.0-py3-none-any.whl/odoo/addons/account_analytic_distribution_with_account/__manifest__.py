# Copyright 2025 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic Distribution With Account",
    "summary": "Adds Account To Account Analytic Distribution Model",
    "version": "16.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/sygel-technology/sy-account-analytic",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "analytic",
    ],
    "data": [
        "views/account_analytic_distribution_views.xml",
    ],
}
