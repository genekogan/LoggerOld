#!/usr/bin/env python
# -*- coding: utf8 -*-

import log
import datetime
import util
import re

##########################
##  Main view page
##########################

def get_log(keyword, date1, date2, location, limit):
	where = []
	if keyword is not None:
		where.append('log like "%'+keyword+'%"')
	if date1 is not None:
		if date2 is None:
			d1 = date1.split("-")
			date2 = datetime.date(int(d1[0]), int(d1[1]), int(d1[2])) 
			date2 += datetime.timedelta(1)
		time1 = str(date1) + ' 05:00'
		time2 = str(date2) + ' 05:00'
		where.append('time > "'+time1+'"')
		where.append('time < "'+time2+'"')
	if location is not None:
		[lat,lng] = location.split(',')
		wstr = '(latitude-' + str(lng) + ')*(latitude-' + str(lng) + ') + (longitude-' + str(lat) + ')*(longitude-' + str(lat) +') < 0.000001'
		where.append(wstr)
	query = 'SELECT rowid, * FROM events '
	if len(where):
		query += "WHERE " + " AND ".join(where) + " ORDER BY time"
	else:
		if limit is None:
			query += " ORDER BY time desc"
		else:
			query += " ORDER BY time desc LIMIT " + str(limit)
	log0 = util.query_db(query)
	return log0

def get_media(date1, date2):
	where = []
	if date1 is not None:
		if date2 is None:
			d1 = date1.split("-")
			date2 = datetime.date(int(d1[0]), int(d1[1]), int(d1[2])) 
			date2 += datetime.timedelta(1)
		time1 = str(date1) + ' 05:00'
		time2 = str(date2) + ' 05:00'
		where.append('time > "'+time1+'"')
		where.append('time < "'+time2+'"')
	query = 'SELECT * FROM media '
	if len(where):	query += "WHERE " + " AND ".join(where) + " ORDER BY time"
	media = util.query_db(query)
	return media
	
def html_log(events):
	html = '''<div id='events'>
		<table width="95%" border=0 cellpadding=4>
			<tr>
				<td width="10%"><h1>Time</h1></td>
				<td width="82%"><h1>Log ('''+str(len(events))+''')</h1></td>
				<td width="8%"></td>
			</tr>'''
	for (idx, event) in enumerate(events):
		(rid, category, time0, lat, lng, log_string) = event
		col = "DDDDEE" if idx%2==0 else "FFFFFF"
		timestamp = util.format_time(time0)			
		if lat is None:
			actions = '<a href="/edit/?id='+str(rid)+'">[e]</a>'		
		else:
			actions = '''<a href="https://maps.google.com/maps?q='''+str(lat)+''','''+str(lng)+'''">[m]</a>
				<a href="javascript:SetEditLog('''+str(rid)+''');">[e]</a>'''		

		links = re.compile('[~!@#\^][^ \'.?,!\(\)]+').findall(log_string)
		for link in links:
			log_string = re.sub(link, '<a href="?keyword='+link[1:]+'">'+link+'</a>', log_string)

		#weblinks = re.compile('\^\((.+)\)').findall(log_string)
		#for link in weblinks:
		#	log_string = re.sub(link, '<a href="http://'+link+'">[web]</a>', log_string)

		html += '''
			<tr bgcolor="'''+col+'''">
				<td>'''+ timestamp +'''</td>
				<td>'''+ log_string +'''</td>
				<td>'''+ actions +'''</td>
			</tr>'''

	html += '</table>'
	html += '</div>'

	# modify log viewbox
	html += '<div id="modifylog" style="display:none; z-index:1;"></div>'
	html += '''<script>
	function HideModifyLog() {
		document.getElementById('modifylog').style.display = 'none';
	}	
	function SetEditLog(idx) { 
		document.getElementById('modifylog').style.display = 'block';
		document.getElementById('modifylog').innerHTML = '<iframe src="/edit/?id='+idx+'" width="100%" height="100%"></iframe><br/><a href="javascript:HideModifyLog();">&nbsp;&nbsp;[close]</a>';
	}	
	</script>'''
	return html


def html_media(media):
	html ='''<div id='media'>'''
	if len(media) > 0:
		skip_thumb = max(1, int(len(media)/4.0))
		for (r, (idx, typ, path, time)) in enumerate(media):
			if  r % skip_thumb == 0:
				html += '<a href="'+path+'" rel="lightbox[logimages]"><img src="'+path+'" width=160 /></a>'
			else:
				html += '<a href="'+path+'" rel="lightbox[logimages]"></a>'
	html += '</div>'
	return html
	
def html_calendar():
	html =  '''<div id='calendar'>
		<table width=280 border=2 cellspacing=0>
		<tr>
			<td width=40><h1>M</h1></td>
			<td width=40><h1>T</h1></td>
			<td width=40><h1>W</h1></td>
			<td width=40><h1>R</h1></td>
			<td width=40><h1>F</h1></td>
			<td width=40><h1>Sa</h1></td>
			<td width=40><h1>Su</h1></td>
		</tr>
		<tr>'''
	date1 = datetime.date(2012, 8, 6)	# the beginning of time
	date2 = datetime.date.today()	
	day_count = (date2 - date1).days + 1
	for d in [d for d in (date1 + datetime.timedelta(n) for n in range(day_count)) if d <= date2]:
		if d.day==1:
			txt = '<b>'+str(d.month)+'</b>/'+str(d.day)
		else:
			txt = str(d.day)
		html += '\t\t<td><a href="?date1='+str(d)+'">'+txt+'</a></td>\n'	
		if d.weekday()==6:
			html += '\t</tr>\n\t<tr>\n'
	html += '\n\t</tr>\n</table>\n</div>'
	return html



##########################
##  Edit logger entry
##########################

def html_edit(id, time0, lat, lng, log0, action):
	html = '<div id="editlog"><h1>'
	# edit an entry
	if action is None:
		(time0, lat, lng, log0) = util.query_db('SELECT time, latitude, longitude, log FROM events WHERE rowid='+str(id))[0]
		html += '''Edit entry #'''+str(id)+'''<p/>
			<form name="editor" action="" method="get">
				<input type="hidden" name="id" value="'''+str(id)+'''">
				<input type="hidden" name="action" value="modify">
				Time: <input type="text" name="time" value="'''+time0+'''">
				<p/>
				Latitude: <input type="text" name="lat" value="'''+str(lat)+'''">
				Longitude: <input type="text" name="lng" value="'''+str(lng)+'''">
				<p/>
				<textarea name="log0" cols="60" rows="10">'''+str(log0)+'''</textarea>
				<p/>
				<input type="submit" value="Edit">
			</form>
			<p/><a href="?action=delete&id='''+str(id)+'''">Delete</a>'''
	# entry modified
	elif str(action) == "modify":
		html += '''<b>Modified</b>:
			<br/>Id: '''+str(id)+'''
			<br/>Time: '''+str(time0)+'''
			<br/>Latitude: '''+str(lat)+'''
			<br/>Longitude: '''+str(lng)+'''
			<br/>Log: '''+str(log0)+'''
			<p/><a href="/">[back]</a>'''
		log.modify_event(id, time0, lat, lng, log0)
	# entry deleted
	elif str(action) == "delete":
		(time0, lat, lng, log0) = util.query_db('SELECT time, latitude, longitude, log FROM events WHERE rowid='+str(id))[0]
		html += '''<b>Deleted:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Time: '''+str(time0)+'''
			<br/>Latitude: '''+str(lat)+'''
			<br/>Longitude: '''+str(lng)+'''
			<br/>Log: '''+str(log0)+'''
			<p/><a href="/">[back]</a>'''
		log.delete_event(id)
	html += '</h1></div>'
	return html

def html_edit_name(id, name, alias, action):
	html = '<div id="editname"><h1>'
	# edit a name
	if action is None:
		(name, alias) = util.query_db('SELECT name, alias FROM people WHERE rowid='+str(id))[0]
		html += '''Edit Name #'''+str(id)+'''<p/>
			<form name="editor" action="" method="get">
				<input type="hidden" name="id" value="'''+str(id)+'''">
				<input type="hidden" name="action" value="modify">
				Name: <input type="text" name="name" value="'''+name+'''">
				Alias: <input type="text" name="alias" value="'''+alias+'''">
				<p/><input type="submit" value="Edit">
			</form>
			<p/><a href="?action=delete&id='''+str(id)+'''">Delete</a>'''
	# name modified
	elif str(action) == "modify":
		html += '''<b>Modified:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Name: '''+name+'''
			<br/>Alias: '''+alias+'''
			<p/><a href="/">[back]</a>'''
		log.modify_name_lookup(id,name,alias)
	# name deleted
	elif str(action) == "delete":
		(name, alias) = util.query_db('SELECT name, alias FROM people WHERE rowid='+str(id))[0]
		html += '''<b>Deleted:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Name: '''+name+'''
			<br/>Alias: '''+alias+'''
			<p/><a href="/">[back]</a>'''
		log.delete_name_lookup(id)
	html += '</h1></div>'
	return html
	
def html_edit_location(id, name, lat, lng, action):
	html = '<div id="editlocation"><h1>'
	# edit a location
	if action is None:
		(name, lat, lng) = util.query_db('SELECT name, latitude, longitude FROM locations WHERE rowid='+str(id))[0]
		html += '''Edit location #'''+str(id)+'''<p/>
			<form name="editor" action="" method="get">
				<input type="hidden" name="id" value="'''+str(id)+'''">
				<input type="hidden" name="action" value="modify">
				Name: <input type="text" name="name" value="'''+name+'''">
				<p/>
				Latitude: <input type="text" name="lat" value="'''+str(lat)+'''">
				Longitude: <input type="text" name="lng" value="'''+str(lng)+'''">
				<p/><input type="submit" value="Edit">
			</form>
			<p/><a href="?action=delete&id='''+str(id)+'''">Delete</a>'''
	# location modified
	elif str(action) == "modify":
		html += '''<b>Modified:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Name: '''+name+'''
			<br/>Latitude: '''+str(lat)+'''
			<br/>Longitude: '''+str(lng)+'''
			<p/><a href="/">[back]</a>'''
		log.modify_location_lookup(id,name,lat,lng)
	# location deleted
	elif str(action) == "delete":
		(name, lat, lng) = util.query_db('SELECT name, latitude, longitude FROM locations WHERE rowid='+str(id))[0]
		html += '''<b>Deleted:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Name: '''+name+'''
			<br/>Latitude: '''+str(lat)+'''
			<br/>Longitude: '''+str(lng)+'''
			<p/><a href="/">[back]</a>'''
		log.delete_location_lookup(id)
	html += '</h1></div>'
	return html
	
def html_mass_edit(backlog_text = None, action = None):
	html = '''<style>
		#backlog {
			background-color:#FFF;
			border:4px solid #5599DD;
			margin:10px;
			margin-top:16px;
			padding:3px;
		}
		#massedit {
			margin:10px;
			margin-top:32px;
		}
	</style>'''
	if backlog_text is not None:
		html += '<table id="backlog" width="96%" border=1 style="margin:32px">'
		html += '<tr><td width="8%"><b>category</b></td><td width="60%"><b>log</b></td><td width="16%"><b>time</b></td><td width="16%"><b>location</b></td></tr>'
		backlog_lines = backlog_text.split('\n')
		for l in backlog_lines:
			logstring = re.compile('^log ').split(l)[-1]
			(logstring, time0, gps, category) = log.process_log_string(logstring, 'log', False)
			print gps
			if gps[0] is None:	location = '<font color="#FF0000">none</font>'
			else:				location = '%0.3f, %0.3f' % gps
			html += '<tr><td>'+category+'</td><td>'+logstring+'</td><td>'+time0+'</td><td>'+location+'</td></tr>'
			if action=='addtolog':	
				log.add_log(logstring, time0, gps, category)
		html += '</table><p>'
	if action != 'addtolog':
		last_log = util.query_db('SELECT rowid, time, log FROM events ORDER BY time DESC LIMIT 1')
		html += '<p><div id="massedit">'
		for l in last_log:	html += '<br>&nbsp;&nbsp;&nbsp;'+str(l[0])+' ('+l[1][:-3]+')  ::  '+l[2]
		html += '''<form name="editor" action="" method="post">
		<textarea id="backlog" name="backlog" cols=110 rows=30 maxlength=2500>'''
		if backlog_text is not None:
			html += backlog_text
		html += '''</textarea><p/>
		<select name="action">
			<option value="validate">validate</option>
			<option value="addtolog">add to log</option>
		</select>
		<input type="submit" value="Submit">&nbsp;&nbsp;&nbsp;&nbsp;
		<input type="button" value="Save" id="save">
		<a href="javascript:removeLimit();">[remove limit]</a>
		</form>
		</div>
		'''
	else:
		html += '<p><a href="/">back</a>'
	return html
