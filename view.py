import sqlite3
import log
import os

HTML_LINK = "/Users/Gene/Code/Python/Projects/Logger/html/logger_front.html"

def open_html_page():
	os.system("open " + HTML_LINK)
	
def format_time(ts):
	months = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
	ts = ts.split(" ")
	dt = ts[0].split("-")
	tm = ts[1].split(":")
	return "%s %s %s:%s" % (months[int(dt[1])-1], dt[2], tm[0], tm[1])

def create_html(DB_NAME, log):
	print "hey"
	f = file(HTML_LINK,'w')
	print f
	f.write('<html><head></head><body>')
	f.write('<table width="68%" border=0 cellpadding=4>')
	f.write('<tr><td width="9%"><b>Time</b></td><td width="7%"><b>Location</b></td><td width="84%"><b>Log</b></td></tr>')
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	
	log = log.split(' ')
	if len(log)==1:
		c.execute('SELECT rowid, * FROM events ORDER BY time desc LIMIT 20')
	else:
		c.execute('SELECT rowid, * FROM events WHERE log like "%'+log[1]+'%" ORDER BY time desc')

	events = c.fetchall()
	events.reverse()
	eidx = 1
	for event in events:
		try:
			if eidx % 2 == 0: col = "EEEEEE"
			else: col = "FFFFFF"
			#col = eidx % 2 == 0 ? "FFFFFF" : "0000FF"
			col1 = format_time(event[1])			
			col2 = '<a href="https://maps.google.com/maps?q='+str(event[2])+','+str(event[3])+'">map</a>'
			col3 = event[4]
			f.write('<tr bgcolor="'+col+'"><td>'+col1+'</td><td>'+col2+'</td><td>'+col3+'</td></tr>')
			eidx += 1		
			print "good"	
		except:
			print "error"
	conn.close()
	f.write("</table>")
	f.write("</body></html>")
	f.close()


#create_html('db/GeneLog.db','/view ~RebanaJohn')

def view_db(query):
	if len(query)==0:
		create_html('db/GeneLog.db')
	else:
		print "yo"