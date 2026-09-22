# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class DelegateMapController(http.Controller):

    @http.route('/delegates/upload_gps', type='json', auth='none', csrf=False, methods=['POST'])
    def upload_gps_locations(self, **kwargs):
        """
        Custom JSON endpoint for delegate GPS upload.
        Expects JSON body with params: {uid, password, db, locations: [{latitude, longitude, timestamp, battery_level, speed}]}
        Uses sudo() to bypass access rights.
        """
        try:
            params = request.params or kwargs or {}
            uid = params.get('uid')
            password = params.get('password')
            db_name = params.get('db')
            locations = params.get('locations', [])

            if not uid or not locations:
                return {'success': False, 'error': 'Missing uid or locations'}

            # Use superuser env to create records
            env = request.env(user=1)  # SUPERUSER_ID
            
            # Verify the delegate exists
            delegate = env['coa.delegate'].browse(int(uid))
            if not delegate.exists():
                return {'success': False, 'error': 'Delegate not found'}

            vals_list = []
            for loc in locations:
                vals_list.append({
                    'delegate_id': int(uid),
                    'latitude': loc.get('latitude', 0),
                    'longitude': loc.get('longitude', 0),
                    'timestamp': loc.get('timestamp'),
                    'battery_level': loc.get('battery_level', 0),
                    'speed': loc.get('speed', 0),
                })

            created = env['delegate.location.log'].sudo().create(vals_list)
            _logger.info("Created %d GPS logs for delegate %s", len(created), uid)
            return {'success': True, 'count': len(created)}

        except Exception as e:
            _logger.error("GPS upload error: %s", str(e))
            return {'success': False, 'error': str(e)}

    @http.route('/delegates/map', type='http', auth='user', website=False)
    def show_delegate_map(self, user_id=None, **kwargs):
        # Query active delegates last known locations
        domain = [('is_active', '=', True), ('last_latitude', '!=', 0), ('last_longitude', '!=', 0)]
        delegates = request.env['coa.delegate'].sudo().search(domain)
        
        delegates_data = []
        for d in delegates:
            delegates_data.append({
                'id': d.id,
                'name': d.name,
                'phone': d.username,
                'lat': d.last_latitude,
                'lng': d.last_longitude,
                'last_seen': d.last_seen.strftime('%Y-%m-%d %H:%M:%S') if d.last_seen else 'N/A'
            })

        # Query history if specific delegate is requested
        history_points = []
        selected_user_name = ""
        if user_id:
            try:
                user_id = int(user_id)
                selected_delegate = request.env['coa.delegate'].sudo().browse(user_id)
                if selected_delegate.exists():
                    selected_user_name = selected_delegate.name
                    logs = request.env['delegate.location.log'].sudo().search(
                        [('delegate_id', '=', user_id)], 
                        limit=100, 
                        order='timestamp desc'
                    )
                    for l in logs:
                        history_points.append({
                            'lat': l.latitude,
                            'lng': l.longitude,
                            'time': l.timestamp.strftime('%H:%M:%S (%m-%d)'),
                            'battery': l.battery_level or 'N/A',
                            'speed': round(l.speed, 1) if l.speed else 0
                        })
            except Exception:
                pass

        # HTML with Leaflet Map
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Delegate Tracking Map</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>
                html, body, #map {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }
                .leaflet-popup-content-wrapper {
                    border-radius: 8px;
                    box-shadow: 0 3px 14px rgba(0,0,0,0.4);
                }
                .leaflet-popup-content {
                    font-size: 13px;
                    line-height: 1.5;
                }
                .info-panel {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    z-index: 1000;
                    background: white;
                    padding: 12px;
                    border-radius: 8px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                    max-width: 250px;
                }
                .info-panel h4 {
                    margin: 0 0 6px 0;
                    font-size: 14px;
                }
                .info-panel p {
                    margin: 4px 0;
                    font-size: 12px;
                    color: #555;
                }
                .badge-active {
                    background-color: #27ae60;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            
            <div class="info-panel">
                <h4>لوحة تتبع المناديب</h4>
                <p>مواقع المناديب الحالية في الميدان.</p>
                """
        
        if selected_user_name:
            html_content += f"<p>عرض مسار الحركة لـ: <b>{selected_user_name}</b></p>"
            html_content += f"<p><a href='/delegates/map'>العودة لخريطة الكل</a></p>"
            
        html_content += """
            </div>

            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                // Initialize Map centered on Cairo, Egypt
                var map = L.map('map').setView([30.0444, 31.2357], 7);

                // Add OpenStreetMap Tile Layer
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                // Parse delegates data passed from Python controller
                var delegates = """ + json.dumps(delegates_data) + """;
                var historyPoints = """ + json.dumps(history_points) + """;

                var markers = [];

                // 1. Draw all delegates last known positions
                delegates.forEach(function(d) {
                    var markerColor = 'blue';
                    var popupText = '<b>المندوب: ' + d.name + '</b><br>' +
                                    'اسم المستخدم: ' + d.phone + '<br>' +
                                    'آخر ظهور: ' + d.last_seen + '<br>' +
                                    '<hr>' +
                                    '<a href="/delegates/map?user_id=' + d.id + '" style="font-weight:bold; color:#c0392b;">عرض مسار الحركة اليوم</a>';
                    
                    var marker = L.marker([d.lat, d.lng]).addTo(map)
                        .bindPopup(popupText);
                    markers.push(marker);
                });

                // 2. Draw movement history line if selected
                if (historyPoints.length > 0) {
                    var latlngs = [];
                    historyPoints.forEach(function(pt, idx) {
                        latlngs.push([pt.lat, pt.lng]);
                        
                        // Add sub-markers for history nodes (only for first few points to avoid clutter)
                        if (idx % 5 === 0 || idx === 0) {
                            var circle = L.circleMarker([pt.lat, pt.lng], {
                                color: idx === 0 ? '#c0392b' : '#34495e',
                                fillColor: idx === 0 ? '#c0392b' : '#7f8c8d',
                                fillOpacity: 0.8,
                                radius: idx === 0 ? 8 : 4
                            }).addTo(map);
                            
                            var label = idx === 0 ? '<b>آخر موقع مسجل</b><br>' : 'نقطة مسار تاريخية<br>';
                            circle.bindPopup(label + 'الوقت: ' + pt.time + '<br>السرعة: ' + pt.speed + ' كم/س<br>البطارية: ' + pt.battery + '%');
                        }
                    });

                    // Draw the line connecting points (history is desc, reverse to draw chronologically)
                    latlngs.reverse();
                    var polyline = L.polyline(latlngs, {color: '#c0392b', weight: 4, opacity: 0.7}).addTo(map);
                    
                    // Zoom map to fit the history trail
                    map.fitBounds(polyline.getBounds());
                } else if (markers.length > 0) {
                    // Zoom map to fit all active markers
                    var group = new L.featureGroup(markers);
                    map.fitBounds(group.getBounds().pad(0.1));
                }
            </script>
        </body>
        </html>
        """
        return html_content
