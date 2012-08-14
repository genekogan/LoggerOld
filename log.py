# CONVENTIONS
# @ locations
# ~ people
# # projects, things, prog languages, tags 
# $() learn
# !() idea
# &() comment
# ?() question, musing
#
# OVERRIDE DATE/TIME
# %(9/8/2012 8:55)
# %(20:20)
#
# ADD NAME LOOKUP
# log \name ~tara ~TaraKelton

import sys
import sqlite3
import datetime
import re
import commands
import urllib2

DB_NAME = '/Users/Gene/Code/Python/Projects/Logger/db/GeneLog.db'

def add_to_log(log, commit, db_name):	
	log = log.replace("\\", "")								# remove slashes
	# add names lookup
	if log.find("/name")==0:
		names = log.split(" ")
		logstring = 'INSERT INTO names_lookup VALUES("'+names[1]+'","'+names[2]+'")'
		if commit:
			conn = sqlite3.connect(db_name)
			c = conn.cursor()
			c.execute(logstring)
			conn.commit()
			conn.close()
		else:
			print logstring
	
	# add entry to log
	else:
		# get metadata
		time = get_timestamp(log)	
		(lat, lng) = get_geolocation()
		
		# format log
		log = substitute_full_names(log, db_name)
		log = re.sub("%\([^\)]+[:/][^\)]+\)", "", log)			# get rid of timestamp override
		log = "\'"+log+"\'"										# encase with quote strings
		logstring = "INSERT INTO events (time,latitude,longitude,log) VALUES ("+time+","+lat+","+lng+","+log+")"

		# execute command or just test it
		if commit:
			conn = sqlite3.connect(db_name)
			c = conn.cursor()
			c.execute(logstring)
			conn.commit()
			conn.close()
		else:
			print logstring

def substitute_full_names(log, db_name):
	conn = sqlite3.connect(db_name)
	c = conn.cursor()
	c.execute('SELECT * FROM names_lookup')
	names = c.fetchall()
	for name in names:
		log = re.sub(name[0], name[1], log)
	conn.commit()
	conn.close()
	return log
	
def get_date_time(log):
	# get actual date and timestamp
	dt = str(datetime.datetime.now())
	dt = dt.split(" ")
	date = dt[0]
	time = dt[1][0:8]
	# override date or time?
	dt = re.compile('%\([^\)]+[:/][^\)]+\)').findall(log)
	if dt:
		d0 = re.compile('(\d+)/(\d+)/(\d+)').findall(dt[0])
		if d0:
			date = "%04d-%02d-%02d" % (int(d0[0][2]), int(d0[0][0]), int(d0[0][1]))
		t0 = re.compile('\d+:\d+').findall(dt[0])
		if t0:
			time = t0[0] + ":00"
	# turn into strings
	date = "\'"+date+"\'"	
	time = "\'"+time+"\'"	
	return (date, time)


def get_timestamp(log):
	# get actual date and timestamp
	dt = str(datetime.datetime.now())
	dt = dt.split(" ")
	date = dt[0]
	time = dt[1][0:8]
	# override date or time?
	dt = re.compile('%\((.+)\)').findall(log)
	if dt:
		d0 = re.compile('(\d+)/(\d+)/(\d+)').findall(dt[0])
		if d0:
			date = "%04d-%02d-%02d" % (int(d0[0][2]), int(d0[0][0]), int(d0[0][1]))
		t0 = re.compile('\d+:\d+').findall(dt[0])
		if t0:
			time = t0[0] + ":00"
	return "\'"+date+" "+time+"\'"	
	
def get_geolocation():
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
		# look up google maps API for lat/lng
		response = urllib2.urlopen(geourl)
		html = response.read()
		lat = re.compile('"lat" : (.+),').findall(html)[0]
		lng = re.compile('"lng" : (.+)').findall(html)[0]
		return (lat, lng)
	except:
		print "no internet connection found, no location code!"
		return ('NULL', 'NULL')
	# reverse geocoding
	# http://maps.googleapis.com/maps/api/geocode/json?latlng=12.97436950,77.5994690&sensor=true


if __name__ == "__main__":
	if len(sys.argv) > 1:
		add_to_log(sys.argv[1], True, DB_NAME)
	else:
		#add_to_log("log %(8/12/2012 19:20) amusing but disappointing confrontation between  a drunk rickshaw driver and a bunch of cops angrily hitting him in the face for stopping traffic, then finally arresting him while onlookers hissed and laughed at him LAT(12.9744762) LNG(77.5993876)", False, DB_NAME)
		add_to_log("%(15:00) %(learned something) !(hello world this is a log test)", False, DB_NAME)
		#add_to_log("/name ~tara ~TaraKelton", False, DB_NAME)
