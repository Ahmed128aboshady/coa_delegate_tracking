# -*- coding: utf-8 -*-
{
    'name': 'COA Sales Delegate Live Tracking & Field Operations',
    'version': '19.0.2.1.7',
    'category': 'Sales',
    'summary': 'Live GPS location tracking, Route planning, Visits, Stock Requests, Expenses and Mobile integration for sales delegates',
    'description': """
COA Sales Delegate Live Tracking & Field Operations
===================================================
- Track field sales representatives in real-time using GPS coordinates.
- Route planning and daily visit management with purpose, transaction counts and geofencing distance validation.
- Van sales and stock transfer requests from warehouses or peer delegate vans.
- Mobile sales orders, collections, and expense submissions.
- Field delegate notes and complaints management.
- Live interactive OpenStreetMap dashboard with historical trail.
    """,
    'author': 'Community of accountants (COA-Egypt)',
    'website': 'https://www.coa-egy.com',
    'support': 'info@coa-egy.com',
    'images': ['static/description/banner.png'],
    'depends': ['base', 'web', 'mail', 'sale', 'stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/coa_delegate_views.xml',
        'views/delegate_visit_views.xml',
        'views/stock_request_views.xml',
        'views/delegate_expense_views.xml',
        'views/delegate_note_views.xml',
        'views/delegate_directive_views.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/delegate_location_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
