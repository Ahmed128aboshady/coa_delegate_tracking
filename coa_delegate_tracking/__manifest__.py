# -*- coding: utf-8 -*-
{
    'name': 'COA Sales Delegate Live Tracking',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Live GPS location tracking and interactive map dashboard for field sales delegates',
    'description': """
COA Sales Delegate Live Tracking
==================================
Track your field sales representatives in real-time using GPS coordinates.
Delegates share their live location from any mobile browser - no app required.
Managers see all delegates pinned on an interactive OpenStreetMap dashboard.
Historical visit log, last-seen timestamp, and customer visit records included.
Perfect for field sales teams, delivery agents, and service technicians.
    """,
    'author': 'Community of accountants (COA-Egypt)',
    'website': 'https://www.coa-egy.com',
    'support': 'info@coa-egy.com',
    'images': ['static/description/banner.png'],
    'depends': ['base', 'web', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/coa_delegate_views.xml',
        'views/delegate_location_views.xml',
        'views/delegate_visit_views.xml',
    ],
    'price': 49.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
