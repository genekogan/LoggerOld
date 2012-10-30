# Logger

[Logger](http://genekogan.com/writing/intro-to-logger.html) is a mostly personal project to create a quick and simple interface to log notes, ideas, commentary, and conversations in an electronic journal to keep an ongoing record of my own personal activities.  Entries are placed into a database along with a timestamp and geolocation (when connected to internet), with various twitter-style reserved characters used to track entities over time. The following conventions apply:

	@ locations
	~ people
	# project, thing, tag
	$ learn
	! idea
	& comment
	? question
	^ web link

The logging utility is written in python and the database is maintained using [SQLite](http://www.sqlite.org/).  Alfred is used to make a convenient shortcut for adding entries.

Viewing and interacting with the database is done through a browser, entirely through the localhost machine via lightweight local webserver setup by [CherryPy](http://www.cherrypy.org/). In the future, analytical tools will be developed to query the database and pull out meaningful statistics and generate summaries.


## Usage

The file util.py has a bunch of utilities for managing databases, including one important one for initializing the events table.  That must be run first (util.py -> initialize_log()).  

Once the log exists, the DB_NAME variable must be hardcoded into each python script to make sure it has the full path to the table, after which the following script will add an entry to the database.

	python /path/to/Logger/log.py "this is the text i want to log"
	
Optionally, the timestamp can be overridden if say the entry is being made later than the time of the event being logged. Must be in format MM/DD/YYYY HH:MM (or just HH:MM if date stays same) in 24-hour time.

	python log.py "this event will have a different timestamp %(8/14/2012 19:22)"
	
Another useful function is the ability to create replacement strings, useful if you want to use a nickname or shorthand for a longer tag. The following example converts all instances of ~john to ~JohnSmith in the database.

	python log.py "/name ~john ~JohnSmith"


## Viewing

The data can be interacted with through a browser. First download and install [CherryPy](http://www.cherrypy.org/).  The following command will launch a local server on which you can see your log data.

	python view.py
	
After launching, open a browser and navigate to "http://127.0.0.1:8080/". The basic interface currently supports viewing entries on specific days and by specific keyword searches. In the future this will be extended with data visualization techniques.


## Extending with Alfred

[Alfred](http://www.alfredapp.com/) is an OSX app which is an alternative to Spotlight.  A handy functionality is extensions which lets you add your own keywords for launching scripts from the search bar. By adding the following script to the extensions and assigning it keyword "log", entries can be added quickly via Alfred, e.g. "log add this to my database"

	python /path/to/Logger/log.py "{query}"


## To-Do

 * override geography
 * reverse geocode
 * js graph tools
