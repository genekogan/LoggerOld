import sys
import sqlite3
import re
import log

def initialize_log(DB_NAME):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('''CREATE TABLE events
	             (time DATETIME, latitude double, longitude double, log text)''')
	conn.commit()
	conn.close()
	print "\nCREATED LOG "+DB_NAME
	
def view_log(DB_NAME):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('SELECT rowid, * FROM events')
	events = c.fetchall()
	print "\nNOW VIEWING LOG "+DB_NAME+"\n=========================="
	for event in events:
		print event
	conn.close()
	
def delete_event(DB1, r):
	conn = sqlite3.connect(DB1)
	c = conn.cursor()
	c.execute('DELETE FROM events WHERE rowid='+str(r))
	conn.commit()
	conn.close()
	
def copy_log_to_log(DB1, DB2, r1=0, r2=0):
	conn = sqlite3.connect(DB1)
	c = conn.cursor()

	if (r2==0):
		c.execute('SELECT rowid, * FROM events')
	else:
		c.execute('SELECT rowid, * FROM events WHERE rowid BETWEEN '+str(r1)+' AND '+str(r2))	
	events = c.fetchall()

	for event in events:
		#ts = event[1].split("-")
		#print ts
		#ts = ts[1] + "/" + ts[2] + "/" + ts[0] + " " + event[2][0:5]
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
#delete_event('db/GeneLog.db',95)
view_log('db/GeneLog.db')
#copy_log_to_log('db/GeneLog.db', 'db/GeneLog.db', 10, 37)
