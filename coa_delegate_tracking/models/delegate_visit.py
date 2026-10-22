# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math

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

    total_visits = fields.Integer(string='Total Visits', compute='_compute_visit_counts', store=True)
    completed_visits = fields.Integer(string='Completed Visits', compute='_compute_visit_counts', store=True)

    @api.depends('visit_ids', 'visit_ids.state')
    def _compute_visit_counts(self):
        for plan in self:
            plan.total_visits = len(plan.visit_ids)
            plan.completed_visits = len(plan.visit_ids.filtered(lambda v: v.state == 'completed'))


class DelegateVisit(models.Model):
    _name = 'delegate.visit'
    _description = 'Delegate Visit'
    _order = 'id asc'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    route_plan_id = fields.Many2one('delegate.route.plan', string='Route Plan', ondelete='cascade', index=True)
    delegate_id = fields.Many2one('coa.delegate', string='Delegate', index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('delegate_id') and vals.get('route_plan_id'):
                plan = self.env['delegate.route.plan'].browse(vals['route_plan_id'])
                if plan.delegate_id:
                    vals['delegate_id'] = plan.delegate_id.id
        return super(DelegateVisit, self).create(vals_list)

    @api.onchange('route_plan_id')
    def _onchange_route_plan_id(self):
        if self.route_plan_id and self.route_plan_id.delegate_id:
            self.delegate_id = self.route_plan_id.delegate_id

    state = fields.Selection([
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='pending', required=True)

    visit_purpose = fields.Selection([
        ('collection', 'تحصيل'),
        ('follow_up', 'متابعة دورية'),
        ('delivery_invoices', 'تسليم فواتير وبضاعة'),
        ('new_customer', 'فتح حساب عميل جديد'),
        ('price_list', 'تقديم عروض أسعار'),
        ('close_accounts', 'مطابقة حسابات'),
        ('marketing', 'عرض منتجات دعائية'),
        ('breakdown', 'حل مشكلة'),
        ('returns', 'استرجاع بضاعة'),
        ('product_review', 'مراجعة منتجات'),
        ('other', 'أخرى')
    ], string='Visit Purpose', default='follow_up')

    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    notes = fields.Text(string='Notes')
    duration = fields.Float(string='Duration (Minutes)', compute='_compute_duration', store=True)
    
    latitude_start = fields.Float(string='Latitude Start', digits=(10, 7))
    longitude_start = fields.Float(string='Longitude Start', digits=(10, 7))
    latitude_end = fields.Float(string='Latitude End', digits=(10, 7))
    longitude_end = fields.Float(string='Longitude End', digits=(10, 7))

    distance_from_customer = fields.Float(
        string='Distance from Customer (m)',
        compute='_compute_distance',
        help='Calculated distance in meters between visit start location and customer coordinates'
    )

    transaction_count = fields.Integer(
        string='عدد المعاملات',
        compute='_compute_transaction_count',
        help='إجمالي عدد المعاملات المنفذة خلال هذه الزيارة'
    )

    def _compute_transaction_count(self):
        for visit in self:
            cnt = 0
            if visit.partner_id and visit.delegate_id and visit.start_time:
                try:
                    visit_dt = visit.start_time
                    if isinstance(visit_dt, str):
                        visit_dt = fields.Datetime.from_string(visit_dt)
                    start_dt = visit_dt.replace(hour=0, minute=0, second=0)
                    end_dt = visit_dt.replace(hour=23, minute=59, second=59)
                    visit_date = visit_dt.date()
                    so_cnt = self.env['sale.order'].search_count([
                        ('partner_id', '=', visit.partner_id.id),
                        ('delegate_id', '=', visit.delegate_id.id),
                        ('date_order', '>=', start_dt),
                        ('date_order', '<=', end_dt)
                    ])
                    pay_cnt = self.env['account.payment'].search_count([
                        ('partner_id', '=', visit.partner_id.id),
                        ('date', '=', visit_date)
                    ])
                    inv_cnt = self.env['account.move'].search_count([
                        ('partner_id', '=', visit.partner_id.id),
                        ('invoice_date', '=', visit_date)
                    ])
                    cnt = so_cnt + pay_cnt + inv_cnt
                except Exception:
                    cnt = 0
            visit.transaction_count = cnt

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                diff = record.end_time - record.start_time
                record.duration = diff.total_seconds() / 60.0
            else:
                record.duration = 0.0

    @api.depends('latitude_start', 'longitude_start', 'partner_id')
    def _compute_distance(self):
        for record in self:
            record.distance_from_customer = 0.0
            partner = record.partner_id
            if hasattr(partner, 'partner_latitude') and hasattr(partner, 'partner_longitude'):
                plat = partner.partner_latitude
                plng = partner.partner_longitude
                vlat = record.latitude_start
                vlng = record.longitude_start
                if plat and plng and vlat and vlng:
                    # Haversine formula
                    R = 6371000.0  # Earth radius in meters
                    dlat = math.radians(plat - vlat)
                    dlng = math.radians(plng - vlng)
                    a = (math.sin(dlat / 2.0) ** 2 +
                         math.cos(math.radians(vlat)) * math.cos(math.radians(plat)) *
                         math.sin(dlng / 2.0) ** 2)
                    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
                    record.distance_from_customer = round(R * c, 2)
