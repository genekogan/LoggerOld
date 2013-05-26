#!/usr/bin/env python
# -*- coding: utf8 -*- 

import sys
import re
import datetime
import commands
import urllib2
import util

def alfred_query(log, category):
	log = log.replace("\\", "")
	if category == "name":								# add name to db
		(name, alias) = log.split(" ")
		add_person(name, alias)
	elif category == "location":						# add location to db
		(name, lat, lng) = log.split(" ")
		add_location(name, lat, lng)
	elif category == "calendar":						# add calendar event to db
		(name, description, datenew, start, end, rm, rt, rw, rr, rf, rs, rsu, until) = process_calendar_string(log)
		add_calendar(name, description, datenew, start, end, rm, rt, rw, rr, rf, rs, rsu, until)
	else:												# add regular log to db
		(log, time, gps, category) = process_log_string(log, category)
		add_log(log, time, gps, category)

def process_log_string(log, category, allow_manual=True):
	time = get_time_manual(log)							# get timestamp from logstring
	if time is None and allow_manual is True:	
		time = get_time_system()
	gps = get_geolocation_manual(log)					# get geolocation frin kigstrubg
	if gps[0] is None and allow_manual is True:	
		gps = get_geolocation_system()
	log = substitute_aliases(log)						# substitue aliases
	log = re.sub("%\([^A-Za-z]+\)", "", log)			# get rid of timestamp override
	log = re.sub('@\(.+\)', "", log)					# get rid of geolocation override
	return (log, time, gps, category)

def process_calendar_string(log):
	log = log.split('"')
	name = substitute_aliases(log[1])
	description = substitute_aliases(log[3])
	rest = log[4].split(' ')
	date = rest[1].split('/')
	if len(date)==2:	date.append(int(datetime.datetime.now().year))	
	datenew = '%04d-%02d-%02d' % (int(date[2]), int(date[0]), int(date[1]))
	time1 = rest[2].split(':')
	time2 = rest[3].split(':')
	start = '%02d:%02d' % (int(time1[0]), int(time1[1]))
	end   = '%02d:%02d' % (int(time2[0]), int(time2[1]))
	rest = rest[4:]
	if len(rest) > 0:
		if '/' in rest[-1]:
			until = rest[-1].split('/')
			if len(until)==2:	until.append(int(datetime.datetime.now().year))
			until = '%04d-%02d-%02d' % (int(until[2]), int(until[0]), int(until[1]))
		else:				
			until = str(datetime.datetime(int(date[2]), int(date[0]), int(date[1])) + datetime.timedelta(7))[0:10]
		(rm, rt, rw, rr, rf, rs, rsu) = [ '1' if r in [r.lower() for r in rest] else None for r in ('m', 't', 'w', 'r', 'f', 's', 'su') ]
	else:
		(rm, rt, rw, rr, rf, rs, rsu, until) = (None, None, None, None, None, None, None, '')
	return (name, description, datenew, start, end, rm, rt, rw, rr, rf, rs, rsu, until)


##########################
##  Logger DB operations
##########################

def add_log(log, time, gps, category):
	if gps[0] is None:	gps = ("NULL", "NULL")
	log = substitute_aliases(log)
	log = re.sub("'", "''", log)
	query = "INSERT INTO events (category, time, latitude, longitude, log) VALUES ('"+category+"','"+time+"',"+str(gps[0])+","+str(gps[1])+",'"+log+"')"
	util.query_db(query)
	
def add_person(name, alias):
	query = "INSERT INTO people (name, alias) VALUES ('"+name+"','"+alias+"')"
	util.query_db(query)

def add_location(name, lat, lng):
	query = "INSERT INTO locations (name, latitude, longitude) VALUES ('"+name+"',"+str(lat)+","+str(lng)+")"
	util.query_db(query)

def delete_event(r):
	query = 'DELETE FROM events WHERE rowid='+str(r)
	util.query_db(query)

def modify_event(id, time, lat, lng, log):
	query = 'UPDATE events SET time="'+str(time)+'", latitude='+str(lat)+', longitude='+str(lng)+', log="'+str(log)+'" WHERE rowid='+str(id)			
	util.query_db(query)
	
def modify_location_lookup(id, name, lat, lng):
	query = 'UPDATE locations SET name="'+name+'", latitude='+str(lat)+', longitude='+str(lng)+' WHERE rowid='+str(id)
	util.query_db(query)
		
def modify_name_lookup(id, name, alias):
	query = 'UPDATE people SET name="'+name+'", alias="'+alias+'" WHERE rowid='''+str(id)
	util.query_db(query)
		
def delete_event(r):
	query = 'DELETE FROM events WHERE rowid='+str(r)
	util.query_db(query)

def delete_name_lookup(r):
	query = 'DELETE FROM people WHERE rowid='+str(r)
	util.query_db(query)

def delete_location_lookup(r):
	query = 'DELETE FROM locations WHERE rowid='+str(r)
	util.query_db(query)
	
def replace_string(s1, s2):
	query = 'SELECT rowid, * FROM events'
	events = util.query_db(query)
	for event in events:
		if s1 in event[5]:
			newevent = re.sub(s1, s2, event[5])
			logstring = "UPDATE events SET log=\"" + newevent + "\" WHERE rowid=" + str(event[0])
			util.query_db(logstring)	

# double-replacing aliases, needs to be fixed
def substitute_aliases(log):
	query = 'SELECT * FROM people'
	names = util.query_db(query)
	for name in names:
		log = re.sub("~"+name[1], "~"+name[0], log)	
	return log


##########################
##  Todo DB operations
##########################

def add_list(name):
	sys_time = get_time_system()
	query = 'INSERT INTO todo_lists (name, created) VALUES ("'+name+'", "'+sys_time+'")'
	util.query_db(query)

def add_todo(description, list_id, parent_id):
	sys_time = get_time_system()
	priority = util.query_db('SELECT max(priority) FROM todo WHERE parent_id='+str(parent_id))[0][0]
	if priority is None:	priority  = 1
	else:					priority += 1
	query = '''INSERT INTO todo (description, list_id, parent_id, priority, status, created) VALUES ("'''+description+'''", '''+str(list_id)+''', '''+str(parent_id)+''', '''+str(priority)+''', 0, "'''+sys_time+'''")'''
	util.query_db(query)

def edit_todo(idx, description):
	query = 'UPDATE todo SET description="'+description+'" WHERE id='+str(idx)
	util.query_db(query)
	
def edit_todo_parent(idx, switch_idx, list_idx):
	query = 'UPDATE todo SET parent_id="'+switch_idx+'" WHERE id='+str(idx)
	util.query_db(query)
	query = 'UPDATE todo SET list_id="'+list_idx+'" WHERE id='+str(idx)
	util.query_db(query)

def delete_todo(idx):
	if idx=="completed":
		completed = util.query_db('SELECT * FROM todo WHERE status=1')
		for c in completed:	delete_todo_idx(c[0])
	else:
		children = util.query_db('SELECT * FROM todo WHERE parent_id='+str(idx))		# delete children
		for child in children:	delete_todo(child[0])
		delete_todo_idx(idx)

def delete_todo_idx(idx):
	(idx, description, list_id, parent_id, priority, status, created, completed) = util.query_db('SELECT * FROM todo WHERE id='+str(idx))[0]			# move self to archive
	if completed is None:	completed = "NULL"
	deleted = get_time_system()
	util.query_db('INSERT INTO todo_archive (id, description, list_id, parent_id, priority, created, completed, archived) VALUES ('+str(idx)+', "'+description+'", '+str(list_id)+', '+str(parent_id)+', '+str(priority)+', "'+created+'", "'+completed+'", "'+deleted+'")')	
	util.query_db('DELETE FROM todo WHERE id='+str(idx))	
	
def toggle_todo(idx, new_status = None):
	if new_status is None:
		status = util.query_db('SELECT status FROM todo WHERE id='+str(idx))[0][0]
		new_status = 1 - status	
	util.query_db(query = 'UPDATE todo SET status='+str(new_status)+' WHERE id='+str(idx))	# update self
	if new_status==1:
		util.query_db('UPDATE todo SET completed="'+get_time_system()+'" WHERE id='+str(idx))
	children = util.query_db('SELECT * FROM todo WHERE parent_id='+str(idx))					# update children
	for child in children:
		toggle_todo(child[0], new_status)

def prioritize_todo(idx):
	(parent_id, priority) = util.query_db('SELECT parent_id, priority FROM todo WHERE id='+str(idx))[0]
	others = util.query_db('SELECT id, priority FROM todo WHERE parent_id='+str(parent_id))
	others = [o for o in others if o[1]<priority]
	if len(others) > 0:
		max_prio = max([o[1] for o in others])
		(other_idx, other_priority) = [o for o in others if o[1]==max_prio][0]
		util.query_db('UPDATE todo SET priority='+str(priority)+' WHERE id='+str(other_idx))
		util.query_db('UPDATE todo SET priority='+str(other_priority)+' WHERE id='+str(idx))


##########################
##  Calendar DB operations
##########################

def add_calendar(name, description, datenew, start, end, rm, rt, rw, rr, rf, rs, rsu, until):
	sys_time = get_time_system()
	name = substitute_aliases(name)
	description = substitute_aliases(description)
	query = "INSERT INTO calendar (name, description, start, end, created) VALUES ('"+name+"','"+description+"','"+datenew+" "+start+"', '"+datenew+" "+end+"', '"+sys_time+"')"
	util.query_db(query)
	if len(until) > 0:			# if there is repetition selected
		repeat_days = [ r[0] for r in enumerate((rm=='1', rt=='1', rw=='1', rr=='1', rf=='1', rs=='1', rsu=='1')) if r[1]==True ]
		date1 = datetime.datetime(int(str(datenew)[0:4]), int(str(datenew)[5:7]), int(str(datenew)[8:10]))
		date2 = datetime.datetime(int(str(until)[0:4]), int(str(until)[5:7]), int(str(until)[8:10]))		
		day_count = (date2 - date1).days + 1
		for d in [d for d in (date1 + datetime.timedelta(n) for n in range(1,day_count)) if d <= date2]:
			if d.weekday() in repeat_days:
				start2 = str(d)[0:10] + ' ' + start
				end2 = str(d)[0:10] + ' ' + end
				query = "INSERT INTO calendar (name, description, start, end, created) VALUES ('"+name+"','"+description+"','"+start2+"', '"+end2+"', '"+sys_time+"')"
				util.query_db(query)

def modify_calendar(id, name, description, start, end):
	query = 'UPDATE calendar SET name="'+name+'", description="'+description+'", start="'+start+'", end="'+end+'" WHERE rowid='''+str(id)
	util.query_db(query)

def delete_calendar(id):
	query = 'DELETE FROM calendar WHERE rowid='+str(id)
	util.query_db(query)
	
	
##########################
##  Time / Geolocation
##########################
	
def get_time_manual(log):
	dt = re.compile('%\((.+)\)').findall(log)
	if dt:
		d0 = re.compile('(\d+)/(\d+)/(\d+)').findall(dt[0])
		if d0:	date = "%04d-%02d-%02d" % (int(d0[0][2]), int(d0[0][0]), int(d0[0][1]))
		else:	date = str(datetime.datetime.now())[0:10]
		t0 = re.compile('\d+:\d+').findall(dt[0])
		if t0:
			t0 = t0[0].split(":")
			time = "%02d:%02d:00" % (int(t0[0]), int(t0[1]))
		else:	time = str(datetime.datetime.now())[11:16]
		timestamp = date + " " + time
	else:	timestamp = None
	return timestamp

def get_time_system():
	sys_time = str(datetime.datetime.now())
	sys_time = re.compile("(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)").findall(sys_time)[0]
	return sys_time
	
def get_geolocation_manual(log):
	(lat, lng) = (None, None)
	geo = re.compile('@\((.+)\)').findall(log)
	if geo:
		gps = re.compile('@\(([^A-Za-z)]+)\)').findall(log)
		if gps:
			(lat, lng) = gps[0].split(",")
			(lat, lng) = (float(lat), float(lng))
		else:
			query = 'SELECT * FROM locations WHERE name="'+geo[0]+'"'
			loc = util.query_db(query)
			if loc:	(lat, lng) = (loc[0][1], loc[0][2])
			else:	(lat, lng) = (None, None)
	return (lat, lng)

def get_geolocation_system():
	try:
		response = commands.getstatusoutput('/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s')
		lines = response[1].split('\n')
		geourl = 'https://maps.googleapis.com/maps/api/browserlocation/json?browser=firefox&sensor=true'
		for i in range(1,len(lines)):
			macs = re.compile('([^ ].+) ([^ ]+:[^ ]+:[^ ]+:[^ ]+:[^ ]+:[^ ]+) ([^ ]+)').findall(lines[i])
			name = macs[0][0]
			mac = macs[0][1]
			ss = macs[0][2]
			geourl += '&wifi=mac:%s%%7Cssid:%s%%7Css:%s' % (mac.replace(":", "-"), name.replace(" ", "%20"), ss)
		response = urllib2.urlopen(geourl)		# look up google maps API for lat/lng
		html = response.read()
		lat = re.compile('"lat" : (.+),').findall(html)[0]
		lng = re.compile('"lng" : (.+)').findall(html)[0]
	except:
		(lat, lng) = (None, None)
		print "error getting geolocation from system"
	return (lat, lng)


##########################
##  Main
##########################

if __name__ == "__main__":
	if len(sys.argv) > 1:
		category = sys.argv[1]
		query = sys.argv[2]
		query = query.decode('utf-8','ignore')
		alfred_query(query, category)
	else:
		#log = "lets test this guy %(3/5/2013 15:15)"
		#add_new_calendar('name', 'description', '2013-05-01 19:00', '2013-05-01 19:30', 1, 0, 1, 0, 1, 0, 0, '2013-05-25')
		#replace_string('~Majesh', '~Mahesh')
		pass