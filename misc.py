# miscellaneous temporary functions
# not needed for logger functionality, can ignore


import re
import util
import log

OLD_DB = '/Users/Gene/Projects/Logger/data/GeneLog.db'

def copy_old_db_to_new_db():
	#util.create_log()
	#util.create_todo()
	
	# copy events
	#events = util.query_db('SELECT * FROM events', OLD_DB)
	#for (r, (time, lat, lng, description)) in enumerate(events):
	#	description = re.sub("'", '"', description)
	#	log.add_log(description, time, [lat,lng], description)
	util.query_db('DROP TABLE people')
	util.query_db('DROP TABLE locations')
	util.query_db('CREATE TABLE people (name TEXT, alias TEXT)')
	util.query_db('CREATE TABLE locations (name TEXT, latitude DOUBLE, longitude DOUBLE)')
	
	# copy names
	names = util.query_db('SELECT * FROM names_lookup', OLD_DB)
	for (r, (s, l)) in enumerate(names):
		s = re.sub('~','',s)
		l = re.sub('~','',l)
		log.add_person(l, s)
	
	# copy locat	ions
	places = util.query_db('SELECT * FROM locations_lookup', OLD_DB)
	for (r, (name, lat, lng)) in enumerate(places):
		print r
		log.add_location(name, lat, lng)

	#log.add_list("current")
	#log.add_list("long-term")
	#log.add_list("tasks")



def disp_tasks():
	util.query_db('DROP TABLE todo2')
	util.query_db('DROP TABLE todo_lists2')
	util.query_db('DROP TABLE todo_archive2')
	util.query_db('CREATE TABLE todo2 (id INTEGER PRIMARY KEY, description TEXT, list_id INTEGER, parent_id INTEGER, priority INTEGER, status INTEGER, created DATETIME, completed DATETIME)')
	util.query_db('CREATE TABLE todo_archive2 (id INTEGER, description TEXT, list_id INTEGER, parent_id INTEGER, priority INTEGER, status INTEGER, created DATETIME, completed DATETIME, archived DATETIME)')
	util.query_db('CREATE TABLE todo_lists2 (id INTEGER PRIMARY KEY, name TEXT, priority INTEGER, created DATETIME, archived DATETIME)')
	
	print "============\nLISTS\n============"
	for tlist in util.get_todo_lists():
		p = 1
		(idx, name, created, archived) = tlist
		query = 'INSERT INTO todo_lists2 (id, name, priority, created) VALUES ('+str(idx)+', "'+name+'", '+str(p)+', "'+created+'")'
		p+=1
		print query
		util.query_db(query)		

	print "============\nTASKS\n============"
	for task in util.get_todo():
		(idx, description, list_id, parent_id, status, created, completed) = task
		if completed is None:	completed = 'NULL'
		
		priority = 1 + util.query_db('SELECT count(*) FROM todo2 WHERE parent_id='+str(parent_id))[0][0]
		
		query = '''INSERT INTO todo2 (id, description, list_id, parent_id, priority, status, created, completed) 
					VALUES ('''+str(idx)+''', "'''+description+'''", '''+str(list_id)+''', '''+str(parent_id)+''', '''+str(priority)+''', '''+str(status)+''', "'''+created+'''", "'''+completed+'''")'''
		print query
		util.query_db(query)
		
	print "============\nARCHIVE\n============"
	for task in util.get_todo_archive():
		(idx, description, list_id, parent_id, created, completed, archived) = task
		if completed is None:	completed = 'NULL'
		priority = 1 + util.query_db('SELECT count(*) FROM todo_archive2 WHERE parent_id='+str(parent_id))[0][0]
		query = '''INSERT INTO todo_archive2 (id, description, list_id, parent_id, priority, status, created, completed, archived) 
				VALUES ('''+str(idx)+''', "'''+description+'''", '''+str(list_id)+''', '''+str(parent_id)+''', '''+str(priority)+''', '''+str(status)+''', "'''+created+'''", "'''+completed+'''", "'''+archived+'''")'''
		print query
		util.query_db(query)

	util.query_db('ALTER TABLE todo RENAME TO todo3')
	util.query_db('ALTER TABLE todo_archive RENAME TO todo_archive3')
	util.query_db('ALTER TABLE todo_lists RENAME TO todo_lists3')
	util.query_db('ALTER TABLE todo2 RENAME TO todo')
	util.query_db('ALTER TABLE todo_archive2 RENAME TO todo_archive')
	util.query_db('ALTER TABLE todo_lists2 RENAME TO todo_lists')
	
	
def fix_locations_names():
	util.query_db('DROP TABLE locations2')
	util.query_db('DROP TABLE people2')
	util.query_db('CREATE TABLE locations2 (id INTEGER PRIMARY KEY, name TEXT, latitude DOUBLE, longitude DOUBLE)')
	util.query_db('CREATE TABLE people2 (id INTEGER PRIMARY KEY, name TEXT, alias TEXT)')

	for loc in util.query_db('SELECT * FROM locations'):
		(name, lat, lng) = loc
		print name
		query = 'INSERT INTO locations2 (name, latitude, longitude) VALUES ("'+name+'", '+str(lat)+', '+str(lng)+')'
		print query
		util.query_db(query)
		print "======================"
		
	for p in util.query_db('SELECT * FROM people'):
		(name, alias) = p
		print name+ ' ' + alias
		query = 'INSERT INTO people2 (name, alias) VALUES ("'+name+'", "'+alias+'")'
		print query
		util.query_db(query)
		print "======================"

	util.query_db('ALTER TABLE locations RENAME TO locations3')
	util.query_db('ALTER TABLE locations2 RENAME TO locations')
	util.query_db('ALTER TABLE people RENAME TO people3')
	util.query_db('ALTER TABLE people2 RENAME TO people')

	#util.query_db('DROP TABLE locations')
	#util.query_db('DROP TABLE people')
	
def fix_locations_names2():
	#util.query_db('ALTER TABLE people RENAME TO people2')
	#util.query_db('ALTER TABLE people3 RENAME TO people')
	#util.query_db('ALTER TABLE locations RENAME TO locations2')
	#util.query_db('ALTER TABLE locations3 RENAME TO locations')
	#util.query_db('DROP TABLE locations2')
	#util.query_db('DROP TABLE people2')
	
#disp_tasks()
fix_locations_names2()