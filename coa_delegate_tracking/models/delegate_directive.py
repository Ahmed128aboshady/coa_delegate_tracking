# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DelegateDirective(models.Model):
    _name = 'delegate.directive'
    _description = 'Delegate Directive / التوجيهات والتعليمات الإدارية للمناديب'
    _order = 'create_date desc, id desc'

    name = fields.Char(string='عنوان التوجيه', required=True)
    body = fields.Text(string='نص التوجيه والتعليمات', required=True)
    
    directive_type = fields.Selection([
        ('urgent', 'عاجل جداً (شريط رئيسي للتنبيه)'),
        ('target', 'هدف بيعي / تارجت'),
        ('general', 'عام / إداري'),
        ('system', 'تنبيه نظام / سيرفر')
    ], string='نوع / أولوية التوجيه', default='urgent', required=True)

    target_type = fields.Selection([
        ('all', 'جميع المناديب'),
        ('specific', 'مناديب محددين بالاسم')
    ], string='نطاق الاستهداف', default='all', required=True)

    delegate_ids = fields.Many2many(
        'coa.delegate',
        'delegate_directive_rel',
        'directive_id',
        'delegate_id',
        string='المناديب المستهدفون'
    )

    is_active = fields.Boolean(string='نشط', default=True, index=True)
    date_start = fields.Datetime(string='تاريخ التفعيل', default=fields.Datetime.now)
    date_end = fields.Datetime(string='تاريخ الانتهاء')
