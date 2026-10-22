# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CoaStockRequest(models.Model):
    _name = 'coa.stock.request'
    _description = 'Delegate Stock / Van Replenishment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Request Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    delegate_id = fields.Many2one(
        'coa.delegate',
        string='المندوب الطالب',
        required=True,
        tracking=True,
        index=True
    )
    request_type = fields.Selection([
        ('warehouse', 'طلب من مستودع رئيسي'),
        ('van', 'طلب من سيارة مندوب زميل')
    ], string='نوع الطلب', default='warehouse', required=True, tracking=True)

    source_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='المستودع المصدر',
        tracking=True
    )
    source_delegate_id = fields.Many2one(
        'coa.delegate',
        string='المندوب الزميل (المصدر)',
        tracking=True
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string='موقع الصرف (المصدر)',
        required=True
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='موقع الاستلام (سيارة المندوب)',
        required=True
    )

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('submitted', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('done', 'تم الصرف والتسليم'),
        ('cancelled', 'ملغي')
    ], string='الحالة', default='draft', tracking=True)

    picking_id = fields.Many2one(
        'stock.picking',
        string='إذن التحويل المخزني',
        readonly=True,
        copy=False
    )
    line_ids = fields.One2many(
        'coa.stock.request.line',
        'request_id',
        string='المنتجات المطلوبة'
    )
    notes = fields.Text(string='ملاحظات الطلب')
    date_request = fields.Datetime(
        string='تاريخ الطلب',
        default=fields.Datetime.now,
        readonly=True
    )

    @api.onchange('delegate_id')
    def _onchange_delegate_id(self):
        if self.delegate_id and self.delegate_id.van_warehouse_id:
            self.dest_location_id = self.delegate_id.van_warehouse_id.lot_stock_id

    @api.onchange('request_type', 'source_warehouse_id', 'source_delegate_id')
    def _onchange_source(self):
        if self.request_type == 'warehouse' and self.source_warehouse_id:
            self.source_location_id = self.source_warehouse_id.lot_stock_id
        elif self.request_type == 'van' and self.source_delegate_id and self.source_delegate_id.van_warehouse_id:
            self.source_location_id = self.source_delegate_id.van_warehouse_id.lot_stock_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('coa.stock.request') or _('New')
        return super(CoaStockRequest, self).create(vals_list)

    def action_submit(self):
        for req in self:
            if not req.line_ids:
                raise UserError(_('يرجى إضافة منتج واحد على الأقل للطلب.'))
            if not req.source_location_id or not req.dest_location_id:
                raise UserError(_('يرجى تحديد موقع المصدر وموقع الوجهة (السيارة).'))
            req.state = 'submitted'

    def action_approve(self):
        for req in self:
            if req.state != 'submitted':
                continue

            # Find picking type for internal transfer
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            if not picking_type:
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'internal')
                ], limit=1)

            if not picking_type:
                raise UserError(_('لم يتم العثور على نوع عملية تحويل داخلي (Internal Transfer).'))

            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': req.source_location_id.id,
                'location_dest_id': req.dest_location_id.id,
                'origin': req.name,
                'move_type': 'direct',
                'move_ids': [
                    (0, 0, {
                        'name': line.product_id.display_name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty_requested,
                        'product_uom': line.product_uom_id.id or line.product_id.uom_id.id,
                        'location_id': req.source_location_id.id,
                        'location_dest_id': req.dest_location_id.id,
                    }) for line in req.line_ids
                ]
            }
            picking = self.env['stock.picking'].create(picking_vals)
            picking.action_confirm()
            req.picking_id = picking.id
            req.state = 'approved'

    def action_validate(self):
        for req in self:
            if req.picking_id and req.picking_id.state not in ['done', 'cancel']:
                # Set quantities done and validate
                for move in req.picking_id.move_ids:
                    move.quantity = move.product_uom_qty
                req.picking_id.button_validate()
            req.state = 'done'

    def action_cancel(self):
        for req in self:
            if req.picking_id and req.picking_id.state not in ['done', 'cancel']:
                req.picking_id.action_cancel()
            req.state = 'cancelled'


class CoaStockRequestLine(models.Model):
    _name = 'coa.stock.request.line'
    _description = 'Delegate Stock Request Line'

    request_id = fields.Many2one('coa.stock.request', string='Stock Request', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='المنتج', required=True)
    qty_requested = fields.Float(string='الكمية المطلوبة', default=1.0, required=True)
    qty_delivered = fields.Float(string='الكمية المسلمة', default=0.0)
    product_uom_id = fields.Many2one('uom.uom', string='وحدة القياس')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
