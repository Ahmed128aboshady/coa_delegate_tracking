# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DelegateExpense(models.Model):
    _name = 'delegate.expense'
    _description = 'Sales Delegate Expense'
    _order = 'date desc, id desc'

    name = fields.Char(string='Description / Reason', required=True)
    delegate_id = fields.Many2one('coa.delegate', string='Delegate', required=True, index=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Amount (SAR)', required=True)
    category = fields.Selection([
        ('fuel', 'Fuel / بنزين'),
        ('food', 'Meals / وجبات'),
        ('maintenance', 'Car Maintenance / صيانة'),
        ('hotel', 'Lodging / إقامة'),
        ('other', 'Other / أخرى')
    ], string='Category', default='fuel', required=True)
    state = fields.Selection([
        ('draft', 'Draft / قيد المراجعة'),
        ('approved', 'Approved / معتمدة'),
        ('rejected', 'Rejected / مرفوضة')
    ], string='Status', default='draft', required=True, index=True)
    notes = fields.Text(string='Notes / ملاحظات')
    receipt_image = fields.Binary(string='Receipt Attachment / إيصال النفقة')

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})
