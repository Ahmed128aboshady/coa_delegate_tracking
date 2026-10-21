# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DelegateNote(models.Model):
    _name = 'delegate.note'
    _description = 'Sales Delegate Note / Feedback'
    _order = 'date desc, id desc'

    delegate_id = fields.Many2one('coa.delegate', string='Delegate', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Related Customer (Optional)')
    date = fields.Datetime(string='Date & Time', required=True, default=fields.Datetime.now)
    note = fields.Text(string='Note / Complaint', required=True)
    state = fields.Selection([
        ('new', 'New / جديدة'),
        ('in_progress', 'In Review / قيد المراجعة'),
        ('resolved', 'Resolved / تم الحل')
    ], string='Status', default='new', required=True, index=True)
    reply = fields.Text(string='Management Response / رد الإدارة')

    def action_mark_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        self.write({'state': 'resolved'})
