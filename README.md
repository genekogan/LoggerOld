# Logger

Logger is a mostly personal project to create a quick and simple interface to log notes, ideas, commentary, and conversations in an electronic journal to keep an ongoing record of my own personal activities.  Entries are placed into a database along with a timestamp and geolocation (when connected to internet), with various twitter-style reserved characters used to track entities over time.

	@ locations
	~ people
	# project, thing, tag
	$ learn
	! idea
	& comment
	? question

The logging utility is written in python and the database is maintained using [SQLite](http://www.sqlite.org/).  Alfred is used to make a convenient shortcut for adding entries.

In the future, analytical tools will be developed to query the database and pull out meaningful statistics and generate summaries.

## Usage

The following script will add an entry to the database.

	python /path/to/Logger/log.py "this is the text i want to log"
	
Optionally, the timestamp can be overridden if say the entry is being made later than the time of the event being logged.

	python log.py "this event will have a different timestamp %(8/14/2012 19:22)"

## Extending with Alfred

[Alfred](http://www.alfredapp.com/) is an OSX app which is an alternative to Spotlight.  A handy functionality is extensions which lets you add your own keywords for launching scripts from the search bar. By adding the following script to the extensions and assigning it keyword "log", entries can be added quickly via Alfred, e.g. "log add this to my database"

	python /path/to/Logger/log.py "{query}"


