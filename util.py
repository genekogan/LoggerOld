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
		print event
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



#initialize_log('db/GeneLog.db')
#copy_log_to_log('ex1.db', 'db/GeneLog.db', 8, 17)
#delete_event('db/GeneLog.db',169)
#for i in range(68, 117):
	#delete_event('db/GeneLog.db', i)
#view_log('db/GeneLog.db', 68, 124)
view_log('db/GeneLog.db')
#delete_name_lookup('db/GeneLog.db', 3)
view_names_lookup('db/GeneLog.db')
view_tags('db/GeneLog.db', '~')
#copy_log_to_log('db/GeneLog.db', 'db/GeneLog.db', 10, 37)
