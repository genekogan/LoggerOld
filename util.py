#!/usr/bin/env python
# -*- coding: utf8 -*- 

import sqlite3
import os.path
import datetime
import re
import log

# name of your database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data/gulag.db')

# wrapper function for interacting with the sqlite database
def query_db(query, db=None):
	if db is None:	db = DB_PATH
	conn = sqlite3.connect(db)
	c = conn.cursor()
	c.execute(query)
	results = c.fetchall()
	conn.commit()
	conn.close()
	return results

def initialize_log():
	create_log()
	create_todo()
	create_calendar()
	create_media()
	
# be careful using these! uncomment if you intend to erase the databases
def create_log():
	print "creating tables for events, people, locations"
	#query_db('DROP TABLE events')
	#query_db('DROP TABLE people')
	#query_db('DROP TABLE locations')
	#query_db('CREATE TABLE events (category TEXT, time DATETIME, latitude DOUBLE, longitude DOUBLE, log TEXT)')
	#query_db('CREATE TABLE people (name TEXT, alias TEXT)')
	#query_db('CREATE TABLE locations (name TEXT, latitude DOUBLE, longitude DOUBLE)')

# be careful using these! uncomment if you intend to erase the databases
def create_todo():
	print "creating tables for todo"
	#query_db('DROP TABLE todo')
	#query_db('DROP TABLE todo_lists')
	#query_db('DROP TABLE todo_archive')
	#query_db('CREATE TABLE todo (id INTEGER PRIMARY KEY, description TEXT, list_id INTEGER, parent_id INTEGER, status INTEGER, created DATETIME, completed DATETIME)')
	#query_db('CREATE TABLE todo_archive (id INTEGER, description TEXT, list_id INTEGER, parent_id INTEGER, created DATETIME, completed DATETIME, archived DATETIME)')
	#query_db('CREATE TABLE todo_lists (id INTEGER PRIMARY KEY, name TEXT, created DATETIME, archived DATETIME)')

def create_calendar():
	print "creating calendar"
	#query_db('DROP TABLE calendar')
	#query_db('CREATE TABLE calendar (id INTEGER PRIMARY KEY, name TEXT, description TEXT, start DATETIME, end DATETIME, created DATETIME)')

def create_media():
	print "creating database of images and sounds"
	query_db('DROP TABLE media')
	query_db('CREATE TABLE media (id INTEGER PRIMARY KEY, type TEXT, filepath TEXT, time DATETIME)')
	
def update_media():
	for root, dirs, files in os.walk('/Users/Gene/Pictures/'):
	    for name in files:
	        if name.lower().endswith((".png", ".jpg", ".jpeg")):
				actual_path = root + '/' + name
				local_path = 'images/' + root[21:] + '/' + name
				file_time = datetime.datetime.fromtimestamp(os.path.getmtime(actual_path))
				query = 'INSERT INTO media (type, filepath, time) VALUES ("image", "'+local_path+'", "'+str(file_time)+'")'
				query_db(query)
				
def format_time(ts):
	months = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
	ts = ts.split(" ")
	dt = ts[0].split("-")
	tm = ts[1].split(":")
	timestring = "%s %s %s:%s" % (months[int(dt[1])-1], dt[2], tm[0], tm[1])
	return timestring
	
#create_media()
#update_media()