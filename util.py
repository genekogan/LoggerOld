import sqlite3
import re
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


# notes to self:
#  hurricane sandy
#  change 369 sudipto to ~sudipto