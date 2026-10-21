# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DelegateLocationLog(models.Model):
    _name = 'delegate.location.log'
    _description = 'Delegate GPS Location Log'
    _order = 'timestamp desc'

    delegate_id = fields.Many2one('coa.delegate', string='Delegate', required=True, ondelete='cascade', index=True)
    latitude = fields.Float(string='Latitude', digits=(10, 7), required=True)
    longitude = fields.Float(string='Longitude', digits=(10, 7), required=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now, required=True, index=True)
    battery_level = fields.Integer(string='Battery Level (%)')
    speed = fields.Float(string='Speed (km/h)')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(DelegateLocationLog, self).create(vals_list)
        # Update last known location on the delegate record for quick queries
        for record in records:
            record.delegate_id.sudo().write({
                'last_latitude': record.latitude,
                'last_longitude': record.longitude,
                'last_seen': record.timestamp
            })
        return records

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        results = super(ResPartner, self).search_read(domain, fields, offset, limit, order, **read_kwargs)
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

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        results = super(ProductProduct, self).search_read(domain, fields, offset, limit, order, **read_kwargs)
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

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delegate_id = fields.Many2one('coa.delegate', string='Sales Delegate')
