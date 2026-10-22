# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    delegate_payment_journal_id = fields.Many2one(
        'account.journal',
        string='Default Payment Journal for Delegates',
        config_parameter='coa_delegate.payment_journal_id',
        domain="[('type', 'in', ('bank', 'cash'))]",
        help='The default cash or bank journal used when delegates record customer payments via the mobile app.'
    )

    enforce_geofencing = fields.Boolean(
        string='Enforce Geofencing Restriction',
        config_parameter='coa_delegate.enforce_geofencing',
        default=False,
        help='If enabled, delegates can only start a visit or confirm an order if they are within the allowed distance from the customer coordinates.'
    )

    geofencing_radius_meters = fields.Integer(
        string='Allowed Geofencing Radius (Meters)',
        config_parameter='coa_delegate.geofencing_radius_meters',
        default=200,
        help='Maximum distance in meters between delegate current GPS location and customer address coordinates.'
    )

    auto_confirm_delegate_orders = fields.Boolean(
        string='Auto-Confirm Mobile Sales Orders',
        config_parameter='coa_delegate.auto_confirm_delegate_orders',
        default=True,
        help='Automatically transition mobile-submitted orders from Quotation to Confirmed Sales Order.'
    )
