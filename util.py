import sys
import sqlite3
import re
from collections import Counter
import log

def initialize_log(DB_NAME):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('''CREATE TABLE events
	             (time DATETIME, latitude double, longitude double, log text)''')
	c.execute('''CREATE TABLE names_lookup
	             (short text, full text)''')
	conn.commit()
	conn.close()
	print "\nCREATED LOG "+DB_NAME
	
def view_log(DB_NAME, r1=0, r2=0):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	if (r2==0):
		c.execute('SELECT rowid, * FROM events ORDER BY time')
	else:
		c.execute('SELECT rowid, * FROM events WHERE rowid BETWEEN '+str(r1)+' AND '+str(r2))
	events = c.fetchall()
	print "\nNOW VIEWING LOG "+DB_NAME+"\n=========================="
	for event in events:
		print str(event[0]) + " | " + event[1] + " | " + event[4] + " | (" + str(event[2]) + ", " + str(event[3]) + ")"
	conn.close()

def view_log(DB_NAME, r1=0, r2=0):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	if (r2==0):
		c.execute('SELECT rowid, * FROM events ORDER BY time')
	else:
		c.execute('SELECT rowid, * FROM events WHERE rowid BETWEEN '+str(r1)+' AND '+str(r2))
	events = c.fetchall()
	print "\nNOW VIEWING LOG "+DB_NAME+"\n=========================="
	for event in events:
		print str(event[0]) + " | " + event[1] + " | " + event[4] + " | (" + str(event[2]) + ", " + str(event[3]) + ")"
	conn.close()
	
def view_names_lookup(DB_NAME):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('SELECT rowid, * FROM names_lookup')
	names = c.fetchall()
	for name in names:
		print str(name[0]) + ": " + name[1] + " => " + name[2]
	conn.close()
	
def view_tags(DB_NAME, char):
	tagset = []
	tagstr = re.compile(char+'([^ ]+)')
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('SELECT rowid, * FROM events ORDER BY time')
	events = c.fetchall()
	for event in events:
		tags = tagstr.findall(event[4])
		for tag in tags:
			tagset.append(tag)
	print tagset
	print Counter(tagset)
	conn.close()
	
def delete_event(DB1, r):
	conn = sqlite3.connect(DB1)
	c = conn.cursor()
	c.execute('DELETE FROM events WHERE rowid='+str(r))
	conn.commit()
	conn.close()

def delete_name_lookup(DB1, r):
	conn = sqlite3.connect(DB1)
	c = conn.cursor()
	c.execute('DELETE FROM names_lookup WHERE rowid='+str(r))
	conn.commit()
	conn.close()
	
# needs to be fixed/validated
def copy_log_to_log(DB1, DB2, r1=0, r2=0):
	conn = sqlite3.connect(DB1)
	c = conn.cursor()

	if (r2==0):
		c.execute('SELECT rowid, * FROM events')
	else:
		c.execute('SELECT rowid, * FROM events WHERE rowid BETWEEN '+str(r1)+' AND '+str(r2))	
	events = c.fetchall()

	for event in events:
		copyevent = event[4]
		ds = re.compile('\(%([^)]+)\)').findall(copyevent)
		#log.add_to_log(copyevent, True, DB2)
		if ds:
			log.add_to_log( re.sub('\(%([^)]+)\) ', '', copyevent) + " %("+ds[0]+")", True, DB2 )
		else:
			print "NONE: ==> " + copyevent
	conn.close()

def modify_event_time(DB_NAME, r, newdate):	
	d0 = re.compile('(\d+)/(\d+)/(\d+)').findall(newdate)
	date = "%04d-%02d-%02d" % (int(d0[0][2]), int(d0[0][0]), int(d0[0][1]))
	t0 = re.compile('\d+:\d+').findall(newdate)
	time = t0[0] + ":00"
	datestring = "UPDATE events SET time=\"" + date + " " + time + "\" WHERE rowid=" + str(r)
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute(datestring)
	conn.commit()
	conn.close()

def view_posts_containing(DB_NAME, tag):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('SELECT rowid, * FROM events ORDER BY time')
	events = c.fetchall()
	for event in events:
		if event[4].find(tag)>-1:
			print event
	conn.close()

def relocate_events(DB_NAME, r1, r2):
	(lat, lng) = log.get_geolocation()
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	for r in range(r1, r2+1):
		latstr = "UPDATE events SET latitude=\"" + lat + "\" WHERE rowid=" + str(r)
		lngstr = "UPDATE events SET longitude=\"" + lng + "\" WHERE rowid=" + str(r)
		c.execute(latstr)
		c.execute(lngstr)
	conn.commit()
	conn.close()

def replace_string(DB_NAME, s1, s2):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('SELECT rowid, * FROM events')
	events = c.fetchall()
	for event in events:
		if s1 in event[4]:
			newevent = re.sub(s1, s2, event[4])
			logstring = "UPDATE events SET log=\"" + newevent + "\" WHERE rowid=" + str(event[0])
			c.execute(logstring)
	conn.commit()
	conn.close()


#initialize_log('db/GeneLog.db')
#copy_log_to_log('ex1.db', 'db/GeneLog.db', 8, 17)
#for i in range(68, 117):
	#delete_event('db/GeneLog.db', i)
#view_log('db/GeneLog.db', 68, 124)
view_names_lookup('db/GeneLog.db')
#view_tags('db/GeneLog.db', '~')
#copy_log_to_log('db/GeneLog.db', 'db/GeneLog.db', 10, 37)
#delete_name_lookup('db/GeneLog.db', 178)

#relocate_events('db/GeneLog.db', 368, 380)

#modify_event_time('db/GeneLog.db', 486, '8/27/2012 22:15')
#replace_string('db/GeneLog.db', '~LNI', '~ElonnaiHickok')
#delete_event('db/GeneLog.db', 803)
view_log('db/GeneLog.db')

#change 369 sudipto to ~sudipto

#view_statistics('db/GeneLog.db')
#view_tags('db/GeneLog.db', '#')
#view_posts_containing('db/GeneLog.db', '~Evan')
#get_timestamp2('db/GeneLog.db')