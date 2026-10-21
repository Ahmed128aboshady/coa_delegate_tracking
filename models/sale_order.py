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
    visit_id = fields.Many2one(
        'delegate.visit',
        string='Visit',
        index=True,
        help='The visit during which this sales order was generated.'
    )

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.delegate_id:
            invoice_vals['delegate_id'] = self.delegate_id.id
        if self.visit_id:
            invoice_vals['visit_id'] = self.visit_id.id
        return invoice_vals


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    delegate_id = fields.Many2one(
        'coa.delegate',
        string='Sales Delegate',
        index=True,
        help='The sales representative / delegate who collected this payment.'
    )
    visit_id = fields.Many2one(
        'delegate.visit',
        string='Visit',
        index=True,
        help='The visit during which this payment was collected.'
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    delegate_id = fields.Many2one(
        'coa.delegate',
        string='Sales Delegate',
        index=True,
        tracking=True,
        help='The sales representative / delegate responsible for this invoice.'
    )
    visit_id = fields.Many2one(
        'delegate.visit',
        string='Visit',
        index=True,
        help='The visit during which this invoice was generated.'
    )
