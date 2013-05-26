#!/usr/bin/env python
# -*- coding: utf8 -*-

import util
import sqlite3
import log

def html_get_todo(toggle, prioritize, delete, description, idx, list_idx, parent_idx, switch_idx, switch_parent, switch_list, close):
	if toggle is not None:
		log.toggle_todo(toggle)
	elif prioritize is not None:
		log.prioritize_todo(prioritize)
	elif delete is not None:	
		log.delete_todo(delete)
	elif switch_idx is not None and switch_parent is not None and switch_list is not None:
		log.edit_todo_parent(switch_idx, switch_parent, switch_list)
	elif description is not None and idx is not None:
		log.edit_todo(idx, description)
	elif description is not None and parent_idx is not None:
		log.add_todo(description, list_idx, parent_idx)

	lists = get_lists()

	html = '''<script language="javascript" type="text/javascript">
	window.onload = function() {'''
	for lst in lists:
		tasks = lists[lst]["tasks"]	
		html += '''OnLoadCheck('listcontents'''+str(lists[lst]["index"])+'''');\n'''	
		for t in tasks:
			html += '''OnLoadCheck('children'''+str(tasks[t].idx)+'''');\n'''	
			if close is not None and tasks[t].parent_idx>0:	
				html += '''Hide('children'''+str(tasks[t].idx)+'''');\n'''
			html += '''$('#view'''+str(tasks[t].idx)+'''').mouseover(function(){ $('#viewoptions'''+str(tasks[t].idx)+'''').css('display', 'inline'); $('#editoptions'''+str(tasks[t].idx)+'''').css('margin-left', '4px'); });\n'''
			html += '''$('#view'''+str(tasks[t].idx)+'''').mouseout(function(){ $('#viewoptions'''+str(tasks[t].idx)+'''').hide(); });\n'''
	html += 'loadNoteBox();'
	html += '''$('#notebox').autosize();'''
	html +=	'}</script>'
	
	# calendar control menu
	html += '''<div id="todocontrols"><ul>
		<li><a href="?close">close</a></li>
		<li><a href="?delete=completed">clear</a></li>
	</ul></div>'''
	
	html += '<div id="main" class="main">'
	for (idxl,l) in enumerate(lists):
		tasks = lists[l]["tasks"]		
		top_level_tasks = [ tasks[t] for t in tasks if tasks[t].parent_idx == 0]

		# top bar of list
		html += '<div id="list'+str(lists[l]["index"])+'" class="top_level_list">'
		html += '<div id="listheader'+str(lists[l]["index"])+'" class="listheader">'
		html += lists[l]["name"]
		html += '<div id="listoptions'+str(lists[l]["index"])+'" class="listoptions">'
		html += '''<a href="javascript:ShowHide('listcontents'''+str(lists[l]["index"])+'''');">...</a>&nbsp;&nbsp; '''
		html += '''<a href="javascript:ShowHide('addtoplevel'''+str(lists[l]["index"])+'''');">+</a>'''
		html += '</div>'
		html += '</div>'	
		html += '<div id="listcontents'+str(lists[l]["index"])+'" class="listcontents">'

		# display lists's tasks
		html += '<ul>'
		for task in top_level_tasks:
			if task.status==0:	html += '<li>'+html_task(task)+'</li>'
			else:				html += '<li class="done">'+html_task(task)+'</li>'
		html += '</ul>'		

		# add top level task to this list
		html += '''<div id="addtoplevel'''+str(lists[l]["index"])+'''" style="display: none;" >
			<form name="input" action="/todo/" method="get" style="display: inline">
			<input type="hidden" name="list_idx" value='''+str(lists[l]["index"])+'''>
			<input type="hidden" name="parent_idx" value=0>
			<input type="text" name="description">
			</form>
			</div>'''
					
		html += '</div>'
		if idxl==0:
			html += html_get_notebox()
		html += '</div>'
	html += '</div>'			
	return html
	
def html_get_notebox():
	html  = '<div id="noteboxdiv">'
	html += '<textarea id="notebox"></textarea>'
	html += '</div>'
	html += '''<script>
	
    
	</script>'''
	
	return html
	
def html_task(task):
	# sort children by priority
	prio = [ c.priority for c in task.children ]
	if task.children is not None:
		task.children = sorted(task.children, key=lambda x: x.priority)
	
	html  = '<div id="task'+str(task.idx)+'" class="task">'
	# view task
	html += '<div id="view'+str(task.idx)+'" class="view">'
	if task.status == 0:	description = task.description
	else:					description = '<strike>'+task.description+'</strike>'
	if len(task.children) > 0:
		html += '''<a href="javascript:ShowHide('children'''+str(task.idx)+'''');">''' + description + '''&nbsp;&nbsp;&nbsp;...</a>'''
	else:
		html += description
	# view options
	html += '<div id="viewoptions'+str(task.idx)+'" class="viewoptions">'
	html += '<a href="/todo/?toggle='+str(task.idx)+'">&#10004;</a>&nbsp;&nbsp;'
	html += '<a href="/todo/?prioritize='+str(task.idx)+'">&#8593;</a>&nbsp;&nbsp;'
	html += '''<a href="javascript:ToggleEdit('''+str(task.idx)+''', 1)">e</a>&nbsp;&nbsp;'''
	html += '''<a href="javascript:ShowHide('addchild'''+str(task.idx)+''''); javascript:Show('children'''+str(task.idx)+''''); ">+</a>'''
	html += '</div>'
	html += '</div>'

	# edit task
	html += '<div id="edit'+str(task.idx)+'" class="edit" style="display: none;" >'
	html += '''<form name="input" action="/todo/" method="get" style="display: inline">
		<input type="text" name="description" value="'''+task.description+'''">
		<input type="hidden" name="idx" value='''+str(task.idx)+'''>
		</form>'''
	# edit options
	html += '<div id="editoptions'+str(task.idx)+'" class="editoptions">'
	html += '<a href="javascript:ToggleEdit('+str(task.idx)+', 0)">e</a>&nbsp;&nbsp;'
	html += '<a href="/todo_edit/?idx_switch='+str(task.idx)+'">s</a>&nbsp;&nbsp;'
	html += '<a href="/todo/?delete='+str(task.idx)+'">-</a>'
	html += '</div>'
	html += '</div>'

	# children tasks
	html += '<div id="children'+str(task.idx)+'" class="children">'
	html += '<ul>'
	for child in task.children:
		if child.status==0:	html += '<li>'+html_task(child)+'</li>'
		else:				html += '<li class="done">'+html_task(child)+'</li>'
		
	# add child
	html += '<div id="addchild'+str(task.idx)+'" class="addchild" style="display: none" >'
	html += '<li>'
	html += '''<form name="input" action="/todo/" method="get" style="display: inline">
		<input type="text" name="description" value="">
		<input type="hidden" name="parent_idx" value='''+str(task.idx)+'''>
		<input type="hidden" name="list_idx" value='''+str(task.list_idx)+'''>
		</form>'''
	html += '''<a href="javascript:ShowHide('addchild'''+str(task.idx)+'''');">[no]</a>'''
	html += '</li>'
	html += '</div>'
	html += '</ul>'
	html += '</div>'
	html += '</div>'
	return html
	
	
def html_modify_task_parent(idx_switch):
	lists = get_lists()	
	html = '<div id="main" class="main_switch_parent">'
	for l in lists:
		tasks = lists[l]["tasks"]		
		top_level_tasks = [ tasks[t] for t in tasks if tasks[t].parent_idx == 0]
		# top bar of list
		html += '<div id="list'+str(lists[l]["index"])+'" class="top_level_list">'
		html += '<div id="listheader'+str(lists[l]["index"])+'" class="listheader">'
		html += lists[l]["name"]
		html += '</div>'
		html += '<div id="listcontents'+str(lists[l]["index"])+'" class="listcontents">'
		# display lists's tasks
		html += '<ul>'
		for task in top_level_tasks:
			if task.status==0:	html += '<li>'+html_modify_task_parent_view(idx_switch, task)+'</li>'
			else:				html += '<li class="done">'+html_modify_task_parent_view(idx_switch, task)+'</li>'
		html += '</ul>'
		html += '</div></div>'
	html += '</div>'	
	return html

def html_modify_task_parent_view(idx_switch, task):
	prio = [ c.priority for c in task.children ]	# sort children by priority
	if task.children is not None:
		task.children = sorted(task.children, key=lambda x: x.priority)
	html  = '<div id="task'+str(task.idx)+'" class="task">'
	description = '<a href="/todo?switch_idx='+str(idx_switch)+'&switch_parent='+str(task.idx)+'&switch_list='+str(task.list_idx)+'">'+task.description+'</a>'
	if task.status == 0:	html += description
	else:					html += '<strike>'+description+'</strike>'	
	html += '<ul>'									# children tasks
	for child in task.children:
		html += '<li>'+html_modify_task_parent_view(idx_switch, child)+'</li>'
	html += '</ul></div>'
	return html	


def get_lists():
	lists = {}
	for (idx, name, priority, created, archived) in util.query_db("SELECT * FROM todo_lists"):
		lists[idx] = { "index":idx, "priority":priority, "name":name, "tasks":{} }			
	for (idx, description, list_idx, parent_idx, priority, status, created, modified) in util.query_db("SELECT * FROM todo ORDER BY parent_id"):
		n = Task(idx, list_idx, parent_idx, priority, description, status)
		lists[list_idx]["tasks"][idx] = n
		if parent_idx != 0:	lists[list_idx]["tasks"][parent_idx].add_child(n)
	return lists

class Task(object):
    def __init__(self, idx, list_idx, parent_idx, priority, description, status):
		self.idx = idx
		self.list_idx = list_idx
		self.parent_idx = parent_idx
		self.priority = priority
		self.description = description
		self.status = status
		self.children = []

    def add_child(self, child):
		self.children.append(child)