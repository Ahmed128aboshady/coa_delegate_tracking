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
    delegate_id = fields.Many2one('coa.delegate', string='Delegate', compute='_compute_delegate_id', store=True, readonly=False, precompute=True)

    @api.depends('route_plan_id.delegate_id')
    def _compute_delegate_id(self):
        for rec in self:
            if rec.route_plan_id and rec.route_plan_id.delegate_id:
                rec.delegate_id = rec.route_plan_id.delegate_id
            elif not rec.delegate_id:
                rec.delegate_id = False

    state = fields.Selection([
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='pending', required=True)

    visit_purpose = fields.Selection([
        ('collection', 'تحصيل'),
        ('follow_up', 'متابعة العميل'),
        ('delivery_invoices', 'تسليم فواتير وكشف حساب'),
        ('new_customer', 'زيارة عميل جديد وتسويق'),
        ('price_list', 'تسليم قوائم الأسعار'),
        ('close_accounts', 'تحصيل وتقفيل حسابات'),
        ('marketing', 'زيارة تسويق الكتروني'),
        ('breakdown', 'كشف أعطال'),
        ('returns', 'استلام مرتجعات'),
        ('product_review', 'متابعة المنتج'),
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

    # Linked Transactions
    order_ids = fields.One2many('sale.order', 'visit_id', string='Sales Orders')
    payment_ids = fields.One2many('account.payment', 'visit_id', string='Payments')
    invoice_ids = fields.One2many('account.move', 'visit_id', string='Invoices')

    transaction_count = fields.Integer(
        string='عدد المعاملات',
        compute='_compute_transaction_count',
        store=True,
        help='إجمالي عدد المعاملات (أوامر بيع + سندات تحصيل + فواتير) المنفذة خلال هذه الزيارة'
    )

    @api.depends('order_ids', 'payment_ids', 'invoice_ids', 'partner_id', 'delegate_id', 'start_time')
    def _compute_transaction_count(self):
        for visit in self:
            cnt = len(visit.order_ids) + len(visit.payment_ids) + len(visit.invoice_ids)
            if cnt == 0 and visit.partner_id and visit.delegate_id and visit.start_time:
                try:
                    visit_date = fields.Date.to_date(visit.start_time)
                    start_dt = fields.Datetime.to_string(fields.Datetime.from_string(visit.start_time).replace(hour=0, minute=0, second=0))
                    end_dt = fields.Datetime.to_string(fields.Datetime.from_string(visit.start_time).replace(hour=23, minute=59, second=59))
                    so_cnt = self.env['sale.order'].search_count([
                        ('partner_id', '=', visit.partner_id.id),
                        ('delegate_id', '=', visit.delegate_id.id),
                        ('date_order', '>=', start_dt),
                        ('date_order', '<=', end_dt)
                    ])
                    pay_cnt = self.env['account.payment'].search_count([
                        ('partner_id', '=', visit.partner_id.id),
                        ('delegate_id', '=', visit.delegate_id.id),
                        ('date', '=', visit_date)
                    ])
                    inv_cnt = self.env['account.move'].search_count([
                        ('partner_id', '=', visit.partner_id.id),
                        ('delegate_id', '=', visit.delegate_id.id),
                        ('invoice_date', '=', visit_date)
                    ])
                    cnt = so_cnt + pay_cnt + inv_cnt
                except Exception:
                    pass
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
