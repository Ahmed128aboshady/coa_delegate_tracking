# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DelegateRoutePlan(models.Model):
    _name = 'delegate.route.plan'
    _description = 'Delegate Route Plan'
    _order = 'date desc, id desc'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    delegate_id = fields.Many2one('coa.delegate', string='Delegate', required=True, ondelete='cascade', index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='State', default='draft', required=True)
    visit_ids = fields.One2many('delegate.visit', 'route_plan_id', string='Visits')

class DelegateVisit(models.Model):
    _name = 'delegate.visit'
    _description = 'Delegate Visit'
    _order = 'id asc'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    route_plan_id = fields.Many2one('delegate.route.plan', string='Route Plan', ondelete='cascade', index=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='pending', required=True)
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    notes = fields.Text(string='Notes')
    duration = fields.Float(string='Duration (Minutes)', compute='_compute_duration', store=True)
    
    latitude_start = fields.Float(string='Latitude Start', digits=(10, 7))
    longitude_start = fields.Float(string='Longitude Start', digits=(10, 7))
    latitude_end = fields.Float(string='Latitude End', digits=(10, 7))
    longitude_end = fields.Float(string='Longitude End', digits=(10, 7))

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                diff = record.end_time - record.start_time
                record.duration = diff.total_seconds() / 60.0
            else:
                record.duration = 0.0
