#!/usr/bin/env python
# -*- coding: utf8 -*-

import logview
import util
import datetime
import nltk
import re
from collections import Counter

NUM_TOP_PEOPLE = 30
NUM_TOP_TAGS = 30
NUM_TOP_LOCATIONS = 30

def get_all_text():
	logs = logview.get_log(None, None, None, None, None)
	
	alltext = ''
	
	all_people = []
	all_tags = []
	all_locations = []
	
	for log in logs:
		# clean up text
		alltext += log[5] + ' '
		log_lower = log[5].lower()
		logp = re.compile('~([A-Za-z0-9]+)').findall(log[5])
		logt = re.compile('#([A-Za-z0-9]+)').findall(log_lower)
		logl = re.compile('@([A-Za-z0-9]+)').findall(log_lower)
		
		post_people = []
		post_tags = []
		post_locations = []
		
		for p in logp:	
			post_people.append(p)
			all_people.append(p)
		for t in logt:	
			post_tags.append(t) 
			all_tags.append(t) 
		for l in logl:	
			post_locations.append(l) 
			all_locations.append(l) 

	all_tokens = Counter(nltk.word_tokenize(alltext))	
	all_people = Counter(all_people)
	all_tags = Counter(all_tags)
	all_locations = Counter(all_locations)

	totalwords = 0
	for t in all_tokens:	totalwords += all_tokens[t]

	# TOKENS
	html =  "<br/>Total tokens: " + str(totalwords) + "\n"
	html += "<br/>Unique tokens: " + str(len(all_tokens)) + "\n"

	html += '<table border=0 width="90%"><tr>\n'
	html += '<td>\n'

	# TOP PEOPLE
	# needs fix: should not count double mentions in single line
	html += "<p/>Unique people: " + str(len(all_people)) + "\n"
	html += '<ul>\n'
	for p in all_people.most_common(NUM_TOP_PEOPLE):
		html += '<br/><li><a href="/?keyword='+p[0]+'">'+p[0]+' ('+str(p[1])+')</li>\n'
	html += '</ul>\n'

	html += '</td><td>\n'

	# TOP TAGS
	html += "<p/>Unique tags: " + str(len(all_tags)) + "\n"
	html += '<ul>\n'
	for p in all_tags.most_common(NUM_TOP_TAGS):
		html += '<br/><li><a href="/?keyword='+p[0]+'">'+p[0]+' ('+str(p[1])+')</li>\n'
	html += '</ul>\n'
	
	html += '</td><td>\n'

	# TOP LOCATIONS
	html += "<p/>Unique locations: " + str(len(all_locations)) + "\n"
	html += '<ul>\n'
	for p in all_locations.most_common(NUM_TOP_LOCATIONS):
		html += '<br/><li><a href="/?keyword='+p[0]+'">'+p[0]+' ('+str(p[1])+')</li>\n'
	html += '</ul>\n'

	html += '</td></tr></table>\n'	
	return html
	
def html_names_lookup():
	query = 'SELECT rowid, * FROM people'
	names = util.query_db(query)
	html = '''
		<table width="33%" border=0 cellpadding=4>
			<tr>
				<td width="10%"><b>Index</b></td>
				<td width="35%"><b>Short</b></td>
				<td width="50%"><b>Name</b></td>
				<td width="5%"></td>
			</tr>
		'''
	for name in names:
		html += '''
			<tr>
				<td>''' + str(name[0])+'''</td>
				<td>''' + name[1] + '''</td>
				<td>''' + name[2] + '''</td>
				<td><a href="/editname/?id='''+str(name[0])+'''">[m]</a></td>
			</tr>
			'''
	html += '</table>'	
	return html

def html_locations_lookup():
	query = 'SELECT rowid, * FROM locations'
	locations = util.query_db(query)
	html = '''
		<table width="33%" border=0 cellpadding=4>
			<tr>
				<td width="8%"><b>Index</b></td>
				<td width="54%"><b>Short</b></td>
				<td width="38%"><b>Location</b></td>
			</tr>
		'''
	for loc in locations:
		html += '''
			<tr>
				<td>''' + str(loc[0])+'''</td>
				<td>''' + loc[1] + '''</td>
				<td>''' + str(loc[2]) + ', ' + str(loc[3]) + '''</td>
				<td><a href="/editlocation/?id='''+str(loc[0])+'''">[m]</a></td>
			</tr>
			'''
	html += '</table>'	
	return html

def html_daily_stats():
	html = '<b>Daily count ('+str(len(logview.get_log(None, None, None, None, None)))+' total)</b>\n'
	date1 = datetime.date(2012, 8, 6)	# the beginning of time
	date2 = datetime.date.today()
	day_count = (date2 - date1).days + 1
	for d in [d for d in (date1 + datetime.timedelta(n) for n in range(day_count)) if d <= date2]:
		log = logview.get_log(None, str(d), None, None, None)
		html += '<br/>'+str(d)+' : '+str(len(log))+'\n'	
	html += '<p/>'
	return html
	
def d3_test():
	html = '''
	
	<script src='http://d3js.org/d3.v2.js'></script>

	<style type='text/css'>

	.chart {
	  margin-left: 42px;
	  font: 10px sans-serif;
	  shape-rendering: crispEdges;
	}

	.chart div {
	  background-color: steelblue;
	  text-align: right;
	  padding: 3px;
	  margin: 1px;
	  color: white;
	}

	.chart rect {
	  stroke: white;
	  fill: steelblue;
	}

	.chart text.bar {
	  fill: white;
	}

	</style>
	
	<script type='text/javascript'>
	var data = [4, 8, 15, 16, 23, 42];
	</script>
	
	<script type='text/javascript'>
	var y = d3.scale.ordinal()
	    .domain(data)
	    .rangeBands([0, 120]);
	</script>
	
	<script type='text/javascript'>
	d3.select(".content").append("div")
	    .attr("class", "chart")
	  .selectAll("div")
	    .data(data)
	  .enter().append("div")
	    .style("width", function(d) { return d * 10 + "px"; })
	    .text(function(d) { return d; });
	</script>
	
	<script type='text/javascript'>
	var x = d3.scale.linear()
	    .domain([0, d3.max(data)])
	    .range(["0px", "420px"]);
	</script>
	
	
	
	<script type='text/javascript'>
	var chart = d3.select(".content").append("svg")
	    .attr("class", "chart")
	    .attr("width", 440)
	    .attr("height", 140)
	    .style("margin-left", "32px") // Tweak alignment…
	  .append("g")
	    .attr("transform", "translate(10,15)");

	chart.selectAll("line")
	    .data(x.ticks(10))
	  .enter().append("line")
	    .attr("x1", x)
	    .attr("x2", x)
	    .attr("y1", 0)
	    .attr("y2", 120)
	    .style("stroke", "#ccc");

	chart.selectAll(".rule")
	    .data(x.ticks(10))
	  .enter().append("text")
	    .attr("class", "rule")
	    .attr("x", x)
	    .attr("y", 0)
	    .attr("dy", -3)
	    .attr("text-anchor", "middle")
	    .text(String);

	chart.selectAll("rect")
	    .data(data)
	  .enter().append("rect")
	    .attr("y", y)
	    .attr("width", x)
	    .attr("height", y.rangeBand());

	chart.selectAll(".bar")
	    .data(data)
	  .enter().append("text")
	    .attr("class", "bar")
	    .attr("x", x)
	    .attr("y", function(d) { return y(d) + y.rangeBand() / 2; })
	    .attr("dx", -3)
	    .attr("dy", ".35em")
	    .attr("text-anchor", "end")
	    .text(String);

	chart.append("line")
	    .attr("y1", 0)
	    .attr("y2", 120)
	    .style("stroke", "#000");
	</script>





	
	'''
	return html