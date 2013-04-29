#!/usr/bin/env python
# -*- coding: utf8 -*-

import csv
import logview

OPENPATHS_DATA = '/Users/Gene/Projects/Logger/external/openPaths/openpaths_genekogan.csv'

def get_logger_gps():
	log = logview.get_log(None, None, None, None, None)
	gps = []
	for row in log:
		(date, lat, lng) = row[2:5]
		if lat is not None and lng is not None:
			gps.append([date,lat,lng])
	return gps
	
def get_openpaths_gps():
	gpsdata = csv.reader(open(OPENPATHS_DATA, 'rb'), dialect='excel', delimiter=';')
	gpsdata.next()
	gps = []
	for row in gpsdata:
		lat = float(row[0])
		lng = float(row[1])
		(date, source) = row[3:5]		
		if date > "2012-09-12 00:00:00":	gps.append([date,lat,lng])
	return gps

def get_gps(log = None):
	if log is None:
		gps  = get_openpaths_gps()
		gps += get_logger_gps()
	else:
		gps = [e[2:5] for e in log if e[3] is not None]
	locations = []
	for event in gps:
		(lat, lng) = event[1:3]
		to_add = True
		for loc in locations:			
			dist = (lat-loc[0])*(lat-loc[0]) + (lng-loc[1])*(lng-loc[1])
			if dist<0.000001:	to_add = False
		if to_add:
			locations.append([lat, lng, 1])
	return locations

def html_get_fullscreen_map():
	html = html_get_map(None, 'fsmap', False)
	html += '''
	<style>
		#overlay {
			position:absolute;
			background-color: #000;
			color: #FFF;
			opacity:0.6;
			filter:alpha(opacity=60); /* For IE8 and earlier */
			padding: 3px 3px;
			margin: 4px 4px;
		}
		.zoomer { margin: 30px 0px;}		
	</style>
	<script>
		map.ui.zoomer.add();
    	map.ui.zoombox.add();
	</script>
	<div id='overlay'>footsteps since 8 Aug 2012</div>
	'''
	return html

def html_get_map(log, name='map', interaction=True):
	locations = get_gps(log)
	if len(locations)==0:	return ''
	min_gps = [ min([l[0] for l in locations]), min([l[1] for l in locations]) ]
	max_gps = [ max([l[0] for l in locations]), max([l[1] for l in locations]) ]
	features = []
	for loc in locations:
		entry = '''{
	        "geometry": { "type": "Point", "coordinates": ['''+str(loc[1])+''','''+str(loc[0])+'''] },
	        "properties": {
				"marker-color": "#D00",
				"marker-symbol": "star-stroked",
				"lat": '''+str(loc[1])+''',
				"lng": '''+str(loc[0])+''',
				"count": '''+str(loc[2])+'''
	        }
	    }'''
		features.append(entry)
	features = 'var features = [' + ','.join(features) + '];'
	html  = '<div id="'+name+'"></div><script>'+features
	html += "var map = mapbox.map('"+name+"');"
	html += '''    
	    map.addLayer(mapbox.layer().id('examples.map-vyofok3q'));
	    var markerLayer = mapbox.markers.layer().features(features);
		map.addLayer(markerLayer);
		var interaction = mapbox.markers.interaction(markerLayer);
	'''
	if interaction:
		html += '''
		interaction.formatter(function(feature) {
			var o = '<h3><a href="?location=' + feature.properties.lat + ',' + feature.properties.lng + '">' +
						'@(' + feature.properties.lng + ',' + feature.properties.lat + ') (' + feature.properties.count + ')' +
						'</a></h3>';
			return o;
	    });'''
	html += '''
	  	map.setExtent([{ 
				lat: '''+str(min_gps[0]-0.0001)+''', 
				lon: '''+str(min_gps[1]-0.0001)+''' 
			}, { 
				lat: '''+str(max_gps[0]+0.0001)+''', 
				lon: '''+str(max_gps[1]+0.0001)+''' 
			}]);
	</script>
	'''
	return html
