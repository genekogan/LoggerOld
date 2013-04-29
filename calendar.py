import log
import util
import datetime

DAY_HEIGHT = 835
DAY_START = 7
DAY_END = 24
days = ( 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' )

def html_get_calendar(date = None, numdays = 7, datenew = None, start = None, end = None, name = None, description = None, rm=None, rt=None, rw=None, rr=None, rf=None, rs=None, rsu=None, until = None, action = None):
	if action=="add":		log.add_calendar(name, description, datenew, start, end, rm, rt, rw, rr, rf, rs, rsu, until)
	elif action=="modify":	log.modify_calendar(idx, name, description, start, end)
	
	# get starting position of calendar
	if date is None:
		startday = datetime.datetime.now() - datetime.timedelta(datetime.datetime.now().weekday())
	else:
		date = date.split('-')
		startday = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
	
	# extra css adjusting size of day columns
	html = '''<style>
		#main { width:'''+str(100+5*(int(numdays)-7))+'''%; }
		.daycontainer { width:'''+str(int(96.0/float(numdays)))+'''%; }
		.day { height:'''+str(DAY_HEIGHT+24)+'''px; }
	</style>	
	'''
	
	# calendar control menu
	html += '''<div id="calendarcontrols"><ul>
		<li><a href="?date='''+str(startday-datetime.timedelta(int(numdays)))[0:10]+'''&numdays='''+str(numdays)+'''"><</a></li>
		<li><a href="?date='''+str(startday+datetime.timedelta(int(numdays)))[0:10]+'''&numdays='''+str(numdays)+'''">></a></li>
		<li><a href="?date='''+str(startday)[0:10]+'''&numdays=7">[7]</a></li>
		<li><a href="?date='''+str(startday)[0:10]+'''&numdays=14">[14]</a></li>
		<li><a href="?date='''+str(startday)[0:10]+'''&numdays=30">[30]</a></li>
		<li><a href="javascript:ShowHide('addnew');">[+]</a></li>
	</ul></div>'''
	html += '<div id="main">'
	
	# column display each day's events
	for i in range(0, int(numdays)):
		day = startday + datetime.timedelta(i)
		html += '<div id="daycontainer" class="daycontainer">'
		html += "<b><center>"+days[int(day.weekday())]+" "+str(day.month)+"/"+str(day.day)+"</center></b>"
		html += '<div id="day'+str(i)+'" class="day">'
		accum_height = 0
		events = get_calendar(str(day)[0:10])
		for e in events:
			start = datetime.datetime(int(e[3][0:4]), int(e[3][5:7]), int(e[3][8:10]), int(e[3][11:13]), int(e[3][14:16]))
			end = datetime.datetime(int(e[4][0:4]), int(e[4][5:7]), int(e[4][8:10]), int(e[4][11:13]), int(e[4][14:16]))
			duration = (end-start).seconds / 3600.0
			top = int(DAY_HEIGHT * (start.hour+start.minute/60.0-DAY_START) / (DAY_END-DAY_START)) - accum_height
			height = int(DAY_HEIGHT * duration / (DAY_END-DAY_START))
			accum_height += height
			
			html += '<div id="event'+str(e[0])+'" class="event" style="position:relative; top:'+str(top)+'; height:'+str(height)+';">'
			html += e[1]+'<br>'
			html += '<font size=2 color="#888">'+e[3][11:]+' - '+e[4][11:]+'</font>'
			html += '<br/><font size=1 color="#555">'+e[2]+'</font>'
			html += '</div>'
			html += '''<script>
			var e = document.getElementById('event'''+str(e[0])+'''');
			e.onclick = function() {
				$('#viewevent .name').text("'''+e[1]+'''");
				$('#viewevent .description').text("'''+e[2]+'''");
				$('#viewevent .start').text("'''+e[3]+'''");
				$('#viewevent .end').text("'''+e[4]+'''");
			    Show('viewevent');
				Hide('modifyevent');
				SetCurrIdx('''+str(e[0])+''');
			};			
			</script>'''
			
		html += '</div></div>'
	html += '</div>'
	
	# Add new event
	html += '''<div id="addnew" style="display:none;">
		Add new event<hr/><p/>
		<form name="input" action="/calendar/" method="get" style="display: inline">
		Name:<br/><textarea name="name" cols=60 rows=1></textarea><p/>
		Description:<br/><textarea name="description" cols=60 rows=5></textarea>
		<p/>
		Date: <input type="text" id="inputDate" name="datenew" size=12 />&nbsp;&nbsp;&nbsp;
		Start: <input type="text" name="start" size=6>&nbsp;&nbsp;&nbsp;
		End: <input type="text" name="end" size=6>&nbsp;&nbsp;&nbsp;
		<a href="javascript:ShowHide('addnewrepeat');">[repeat]</a>
		<div id="addnewrepeat" style="display:none;">
		M<input type="checkbox" name="rm" value=1>&nbsp;&nbsp;
		T<input type="checkbox" name="rt" value=1>&nbsp;&nbsp;
		W<input type="checkbox" name="rw" value=1>&nbsp;&nbsp;
		R<input type="checkbox" name="rr" value=1>&nbsp;&nbsp;
		F<input type="checkbox" name="rf" value=1>&nbsp;&nbsp;
		Sa<input type="checkbox" name="rs" value=1>&nbsp;&nbsp;
		Su<input type="checkbox" name="rsu" value="rsu">
		<p/>		
		Until: <input type="text" id="inputUntil" name="until" size=12 />
		</div>
		<input type="hidden" name="action" value="add">
		<p/><input type="Submit" value="submit">
		</form>
		<p/>
		<p/><p/><a href="javascript:Hide('addnew');">[close]</a>
	</div>'''
	
	# View/modify events
	html += '''<div id="viewevent" style="display:none;">
		<span class="name">Name</span><hr/><p/>
		<font color="#ccc">
		<span class="description">Description</span>
		</font><p/>
		Start: <span class="start">start</span>&nbsp;&nbsp;&nbsp;&nbsp;
		End: <span class="end">end</span>&nbsp;&nbsp;&nbsp;&nbsp;
		<p/><a href="javascript:SetModify();">[edit]</a>
		<p/><p/><a href="javascript:Hide('viewevent');">[close]</a>		
	</div>
	<div id="modifyevent" style="display:none;"></div>'''
	return html

def html_edit_calendar(id, name = None, description = None, start = None, end = None, action = None):
	html = '<div id="editcalendar"><h1>'
	# edit a name
	if action is None:
		(name, description, start, end) = util.query_db('SELECT name, description, start, end FROM calendar WHERE rowid='+str(id))[0]
		html += '''Edit Calendar #'''+str(id)+'''<p/>
			<form name="editor" action="" method="get">
				<input type="hidden" name="id" value="'''+str(id)+'''">
				<input type="hidden" name="action" value="modify">
				Name:<br/><textarea name="name" cols=60 rows=1>'''+name+'''</textarea><p/>
				Description:<br/><textarea name="description" cols=60 rows=5>'''+description+'''</textarea>
				<p/>
				<p/>Start: <input type="text" name="start" value="'''+start+'''">
				End: <input type="text" name="end" value="'''+end+'''">
				<p/><input type="submit" value="Edit">
			</form>
			<p/><a href="?action=delete&id='''+str(id)+'''">Delete</a>'''
	# name modified
	elif str(action) == "modify":
		html += '''<b>Modified:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Name: '''+name+'''
			<br/>Description: '''+description+'''
			<br/>Start: '''+start+'''
			<br/>End: '''+end
		log.modify_calendar(id, name, description, start, end)
	# name deleted
	elif str(action) == "delete":
		(name, description, start, end) = util.query_db('SELECT name, description, start, end FROM calendar WHERE rowid='+str(id))[0]
		html += '''<b>Deleted:</b>
			<br/>Id: '''+str(id)+'''
			<br/>Name: '''+name+'''
			<br/>Description: '''+description+'''
			<br/>Start: '''+start+'''
			<br/>End: '''+end
		log.delete_calendar(id)
	html += '</h1></div>'
	return html
	
def get_calendar(date):
	query = 'SELECT * FROM calendar'
	if date is not None:	query += ' WHERE start like "'+date+'%"'
	events = util.query_db(query)
	return events
