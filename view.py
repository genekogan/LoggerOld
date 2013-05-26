#!/usr/bin/env python
# -*- coding: utf8 -*-

import cherrypy
import datetime
import os.path
import log
import mapbox
import logview
import stats
import util
import todo
import calendar

def make_page(content, css = None, js = None, navbar = False):
	html = '''<html><head>
		<title>Logger</title>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
		<link href="/css/style.css" rel="stylesheet" type="text/css"></link>'''
	if css is not None:
		for c in css:	html += '<link href="/css/'+c+'.css" rel="stylesheet" type="text/css"></link>'
	if js is not None:
		for j in js:	html += '<script src="/js/'+j+'.js"></script>'
	html += '</head><body>'
	html += content
	if navbar:
		html += '''<div id="navbar"><ul>
			<li><a href="/">logger</a></li>
			<li><a href="/massedit">edit</a></li>
			<li><a href="/todo">todo</a></li>
			<li><a href="/calendar">calendar</a></li>
			<li><a href="/stats">stats</a></li>
			<li><a href="/map">map</a></li>
		</ul></div>'''
	html += '</body></html>'
	return html
	
class LogPage:
    def index(self, keyword = None, date1 = None, date2 = None, location = None, limit = None):
		# get log according to parameters given
		if keyword is None and date1 is None and location is None:
			date1 = str(datetime.date.today())
			if len(logview.get_log(None, date1, None, None, limit))==0:
				date1 = str(datetime.date.today() - datetime.timedelta(1))
		log = logview.get_log(keyword, date1, date2, location, limit) 
		media = logview.get_media(date1, date2)
		html = '<div id="left">'
		html += logview.html_log(log)
		html += '</div>'
		html += '<div id="right">'
		html += mapbox.html_get_map(log)
		html += logview.html_media(media)
		html += logview.html_calendar()
		html += '</div>'
		html = make_page(html, ['mapbox', 'lightbox'], ['mapbox', 'jquery-1.7.2.min', 'lightbox'], True)
		return html
    index.exposed = True

class EditPage:
    def index(self, id = None, time = None, lat = None, lng = None, log0 = None, action = None):
		html = logview.html_edit(id, time, lat, lng, log0, action)
		html = make_page(html, None, None, False)
		return html
    index.exposed = True

class EditNamePage:
    def index(self, id = None, name = None, alias = None, action = None):
		html = logview.html_edit_name(id, name, alias, action)
		html = make_page(html, None, None, False)
		return html
    index.exposed = True

class EditLocationPage:
    def index(self, id = None, name = None, lat = None, lng = None, action = None):
		html = logview.html_edit_location(id, name, lat, lng, action)
		html = make_page(html, None, None, False)
		return html
    index.exposed = True

class MassEditPage:
    def index(self, backlog = None, action = None):
		html = logview.html_mass_edit(backlog, action)
		html = make_page(html, None, ['massedit'], True)
		return html
    index.exposed = True

class MapPage:
    def index(self):
		html = mapbox.html_get_fullscreen_map()
		html = make_page(html, ['mapbox'], ['mapbox'], True)
		return html
    index.exposed = True

class StatsPage:
    def index(self):
		html =  '<div class="analysis">'
		html += stats.html_names_lookup()
		html += '<p/>'
		html += stats.html_locations_lookup()
		html += stats.get_all_text()
		html += '<p/>'
		html += stats.html_daily_stats()
		html += '</div>'
		html = make_page(html, None, None, True)
		return html
    index.exposed = True

class D3TestPage:			# experimental
    def index(self):
		html = stats.d3_test()
		html = make_page(html, None, ['d3.v3'], True)
		return html
    index.exposed = True

class TodoPage:
    def index(self, toggle = None, prioritize = None, delete = None, description = None, idx = None, list_idx = None, parent_idx = None, switch_idx = None, switch_parent = None, switch_list = None, close = None):
		html = todo.html_get_todo(toggle, prioritize, delete, description, idx, list_idx, parent_idx, switch_idx, switch_parent, switch_list, close)
		html = make_page(html, ['todo'], [ 'jquery.min', 'jquery.autosize-min', 'todo'], True)
		return html
    index.exposed = True

class TodoEditParentPage:
    def index(self, idx_switch):
		html = todo.html_modify_task_parent(idx_switch)
		html = make_page(html, ['todo'], None, True)
		return html
    index.exposed = True

class CalendarPage:
    def index(self, date = None, numdays = 7, datenew = None, start = None, end = None, name = None, description = None, rm=None, rt=None, rw=None, rr=None, rf=None, rs=None, rsu=None, until = None, action = None):
		html = calendar.html_get_calendar(date, numdays, datenew, start, end, name, description, rm, rt, rw, rr, rf, rs, rsu, until, action)
		html = make_page(html, ['calendar', 'jsDatePick_ltr.min'], ['jquery.min', 'jsDatePick.min.1.3', 'calendar'], True)
		return html
    index.exposed = True

class EditCalendarPage:
    def index(self, id = None, name = None, description = None, start = None, end = None, action = None):
		html = calendar.html_edit_calendar(id, name, description, start, end, action)
		html = make_page(html, None, None, False)
		return html
    index.exposed = True


# CherryPy startup
root = LogPage()
root.edit = EditPage()
root.editname = EditNamePage()
root.editlocation = EditLocationPage()
root.massedit = MassEditPage()
root.stats = StatsPage()
root.d3 = D3TestPage()
root.map = MapPage()
root.todo = TodoPage()
root.todo_edit = TodoEditParentPage()
root.calendar = CalendarPage()
root.editcalendar = EditCalendarPage()
lconfig = os.path.join(os.path.dirname(__file__), 'lconfig.conf')

if __name__ == '__main__':
    cherrypy.quickstart(root, config=lconfig)
else:
    cherrypy.tree.mount(root, config=lconfig)

