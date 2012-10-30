import cherrypy
import datetime
import os.path
import sqlite3
import log
import re

from collections import Counter


DB_NAME = '/Users/Gene/Code/Python/Projects/Logger/db/GeneLog.db'

def format_time(ts):
	months = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
	ts = ts.split(" ")
	dt = ts[0].split("-")
	tm = ts[1].split(":")
	return "%s %s %s:%s" % (months[int(dt[1])-1], dt[2], tm[0], tm[1])


def get_log(keyword, date1, date2):
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
	
	query = 'SELECT rowid, * FROM events '
	if len(where):
		query += "WHERE " + " AND ".join(where) + " ORDER BY time"
	else:
		query += " ORDER BY time desc LIMIT 30"
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute(query)
	log = c.fetchall()
	conn.close()
	return log
	

def html_names_lookup():
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('SELECT rowid, * FROM names_lookup')
	names = c.fetchall()
	conn.close()

	html = '''
		<table width="33%" border=0 cellpadding=4>
			<tr>
				<td width="10%"><b>Index</b></td>
				<td width="35%"><b>Short</b></td>
				<td width="55%"><b>Name</b></td>
			</tr>
		'''
	for name in names:
		html += '''
			<tr>
				<td>''' + str(name[0])+'''</td>
				<td>''' + name[1] + '''</td>
				<td>''' + name[2] + '''</td>
			</tr>
			'''
	html += '</table>'	
	return html
				

def html_calendar():
	html =  '<table width=280 border=2 cellspacing=0>\n\t<tr>'
	html += '''
			<td width=40><h1>M</h1></td>
			<td width=40><h1>T</h1></td>
			<td width=40><h1>W</h1></td>
			<td width=40><h1>R</h1></td>
			<td width=40><h1>F</h1></td>
			<td width=40><h1>Sa</h1></td>
			<td width=40><h1>Su</h1></td>
		</tr>\n\t<tr>\n
		'''
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
	html += '\n\t</tr>\n</table>'
	return html
	
	
def html_tags(char):
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


def html_log(events):
	html = '''
		<table width="95%" border=0 cellpadding=4>
			<tr>
				<td width="10%"><h1>Time</h1></td>
				<td width="82%"><h1>Log ('''+str(len(events))+''')</h1></td>
				<td width="8%"></td>
			</tr>
		'''

	for (idx, event) in enumerate(events):
		if idx%2==0: col = "DDDDEE"
		else: col = "FFFFFF"

		timestamp = format_time(event[1])			
		log_string = event[4]
		actions = '''
			<a href="https://maps.google.com/maps?q='''+str(event[2])+''','''+str(event[3])+'''">[m]</a>
			<a href="/edit/?id='''+str(event[0])+'''">[e]</a>
			'''		
		
		links = re.compile('[~!@#][^ \.?,!\(\)]+').findall(log_string)
		for link in links:
			log_string = re.sub(link, '<a href="?keyword='+link[1:]+'">'+link+'</a>', log_string)

		html += '''
			<tr bgcolor="'''+col+'''">
				<td>'''+ timestamp +'''</td>
				<td>'''+ log_string +'''</td>
				<td>'''+ actions +'''</td>
			</tr>
			'''
	html += '</table>'
	return html
	

def make_page(content):
	html = '''
		<html>
			<head>
				<title>Logger</title>
				<style media="screen" type="text/css">
				
					body,html {
						background-color: #364154;
					    font-family: "Georgia", "Verdana";
						font-weight: normal;
						border: 0px;
						margin: 0px;
						padding: 0px;
					}
					h1 {
						font-size: 16px;
						color: #fff;
					}
					h2 {
						font-size: 16px;
					}
					.left, .right {
					  	float: left;
					  	margin: 0px;
						padding: 8px 8px;
						margin-top: 12px;
						margin-bottom: 40px;
					}
					.left {
						width: 60%;
					}
					.right {
						width: 35%;
					}
					a, a:visited {
						color: #bb22bb;
						text-decoration: none;
					}
					a:hover {
						color: #d3832d;
					    text-decoration: underline;
					}
					
				</style>
			</head>
			<body>
		'''
	html += content
	html += '''
			</body>
			</html>
		'''
	return html
	
def html_log_page(keyword, date1, date2):
	log = get_log(keyword, date1, date2) 
	html = '<div class="left">'
	html += html_log(log)
	html += '</div>'
	html += '<div class="right">'
	html += '''
	<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
	src="https://maps.google.com/maps?q=12.9753404,77.6414037&amp;ie=UTF8&amp;t=m&amp;z=14&amp;ll=12.97534,77.641404&amp;output=embed"></iframe><br />
	<p/>
	'''
	html += html_calendar()
	html += '</div>'
	return html

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
	
# UTILITIES
def delete_event(r):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('DELETE FROM events WHERE rowid='+str(r))
	conn.commit()
	conn.close()
	
def modify_event(id,time,lat,lng,log):
	query = '''UPDATE events SET
		time="'''+str(time)+'''",
		latitude='''+str(lat)+''',
		longitude='''+str(lng)+''',
		log="'''+str(log)+'''"
		WHERE rowid='''+str(id)			
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute(query)
	conn.commit()
	conn.close()

def delete_name_lookup(r):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()
	c.execute('DELETE FROM names_lookup WHERE rowid='+str(r))
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

class LogPage:
    def index(self, keyword = None, date1 = None, date2 = None):
		html = html_log_page(keyword, date1, date2)
		html = make_page(html)
		return html
    index.exposed = True

class EditPage:
    def index(self, id = None, time = None, lat = None, lng = None, log = None, action = None):
		conn = sqlite3.connect(DB_NAME)
		c = conn.cursor()
		c.execute('SELECT rowid, * FROM events WHERE rowid='+str(id))
		entry = c.fetchall()
		conn.close()

		rowid0 = entry[0][0]
		time0 = entry[0][1]
		lat0 = entry[0][2]
		lng0 = entry[0][3]
		log0 = entry[0][4]
		
		html = '<div class="left"><h1>'
		
		if action is None:
			html += '''Edit entry #'''+str(rowid0)+'''<p/>
				<form name="editor" action="" method="get">
					<input type="hidden" name="id" value="'''+str(rowid0)+'''">
					<input type="hidden" name="action" value="modify">
					Time: <input type="text" name="time" value="'''+str(time0)+'''">
					<p/>
					Latitude: <input type="text" name="lat" value="'''+str(lat0)+'''">
					Longitude: <input type="text" name="lng" value="'''+str(lng0)+'''">
					<p/>
					<textarea name="log" cols="70" rows="10">'''+str(log0)+'''</textarea>
					<p/>
					<input type="submit" value="Edit">
				</form>
				<p/>
				<a href="?action=delete&id='''+str(rowid0)+'''">Delete</a>
				'''
				
		elif str(action) == "modify":
			html += '''<b>Original:</b>
				<br/>Id: '''+str(rowid0)+'''
				<br/>Time: '''+str(time0)+'''
				<br/>Latitude: '''+str(lat0)+'''
				<br/>Longitude: '''+str(lng0)+'''
				<br/>Log: '''+str(log0)+'''
				<p/>
				<b>New</b>:
				<br/>Id: '''+str(id)+'''
				<br/>Time: '''+str(time)+'''
				<br/>Latitude: '''+str(lat)+'''
				<br/>Longitude: '''+str(lng)+'''
				<br/>Log: '''+str(log)+'''
				<p/>
				<a href="/">[back]</a>
				'''
			modify_event(id,time,lat,lng,log)
		
		elif str(action) == "delete":
			html += '''<b>Deleted:</b>
				<br/>Id: '''+str(rowid0)+'''
				<br/>Time: '''+str(time0)+'''
				<br/>Latitude: '''+str(lat0)+'''
				<br/>Longitude: '''+str(lng0)+'''
				<br/>Log: '''+str(log0)+'''
				<p/>
				<a href="/">[back]</a>
				'''
			delete_event(rowid0)
		
		html += '<h1></div>'
		html = make_page(html)
		return html
    index.exposed = True
	

# CherryPy startup
root = LogPage()
root.edit = EditPage()
lconfig = os.path.join(os.path.dirname(__file__), 'lconfig.conf')
if __name__ == '__main__':
    cherrypy.quickstart(root, config=lconfig)
else:
    cherrypy.tree.mount(root, config=lconfig)

