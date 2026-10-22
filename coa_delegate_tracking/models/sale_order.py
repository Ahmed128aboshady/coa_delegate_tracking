# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delegate_id = fields.Many2one(
        'coa.delegate',
        string='Sales Delegate',
        index=True,
        tracking=True,
        help='The sales representative / delegate who took or generated this order.'
    )
