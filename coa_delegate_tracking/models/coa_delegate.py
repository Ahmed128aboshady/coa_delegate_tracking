# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CoaDelegate(models.Model):
    _name = 'coa.delegate'
    _description = 'COA Sales Delegate'
    _order = 'name asc'

    name = fields.Char(string='Name', required=True)
    username = fields.Char(string='Username', required=True, index=True)
    password = fields.Char(string='Password', required=True)
    is_active = fields.Boolean(string='Active', default=True, index=True)
    
    last_latitude = fields.Float(string='Last Latitude', digits=(10, 7))
    last_longitude = fields.Float(string='Last Longitude', digits=(10, 7))
    last_seen = fields.Datetime(string='Last Seen')

    _sql_constraints = [
        ('username_uniq', 'unique(username)', 'The username must be unique!')
    ]

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        results = super(CoaDelegate, self).search_read(domain, fields, offset, limit, order, **read_kwargs)
        if results:
            fields_to_check = list(results[0].keys())
            fields_info = self.fields_get(fields_to_check, ['type'])
            for record in results:
                for key, val in list(record.items()):
                    if val is False:
                        field_type = fields_info.get(key, {}).get('type')
                        if field_type in ['char', 'text', 'html', 'selection']:
                            record[key] = ""
        return results
