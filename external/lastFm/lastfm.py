#!/usr/bin/env python
###############################################################################
##
## digger - Digging into some data mines
## Copyright (C) 2010  Thammi
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## 
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

import os
import json
import urllib
from warnings import warn
import os.path
import json
#from json_batch import save_batch

#env_var = '615855ad10248d25b451876e2cef0174'
#if env_var in os.environ:
#    API_KEY = os.environ[env_var]
#else:
#    API_KEY = ''
#    warn("No last.fm API key set, use " + env_var)

#77c98373ac2234c4ef3646327b2357bf
API_KEY = '615855ad10248d25b451876e2cef0174'


# TODO: poor stack ...
# TODO: we are missing tracks if the user is scrobbling while we fetch
def get_scrobbles(user, count=200, page=1, max_pages=1, tries=3):
    print "Fetching page", page

    query = urllib.urlencode({
        'format': 'json',
        'method': 'user.getRecentTracks',
        'api_key': API_KEY,
        'user': user,
        'limit': count,
        'page': page,
        })

    base_url = "http://ws.audioscrobbler.com/2.0/"

    try:
        res = urllib.urlopen("%s?%s" % (base_url, query))
    except IOError:
        warn("Exception while fetching the page")
        if tries > 1:
            # retry
            return get_scrobbles(user, count, page, max_pages, tries-1)
        else:
            # give up
            warn("No more tries left, aborting")
            return []

    if res.getcode() < 300:
        raw = json.load(res)

        if 'error' in raw:
            print "Error: " + raw['message']
            return []

        base = raw['recenttracks']
        scrobbles = base['track']
        pages = int(base[u'@attr']['totalPages'])

        if max_pages > 1 and page < pages:
            scrobbles.extend(get_scrobbles(user, count, page+1, max_pages-1))

        return scrobbles
    else:
        print "Unable to fetch: %i '%s'" % (res.getcode(), res.info())
        return []


def change_batch(change, file_name):
    if os.path.exists(file_name):
        # read in old data
        try:
            inp = file(file_name)
            batch = json.load(inp)
            inp.close()
        except:
            warn("Couldn't load old data")
            batch = {}
    else:
        batch = {}

    # apply changes
    change(batch)

    # writing back
    out = file(file_name, 'w')
    json.dump(batch, out)
    out.close()

def update_batch(update, file_name):
    change_batch(lambda batch: batch.update(update), file_name)

def save_batch(item, data, file_name):
    def save(batch):
        batch[item] = data

    change_batch(save, file_name)

def load_batch(file_name):
    inp = file(file_name)
    data = json.load(inp)
    inp.close()
    return data


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print "Please specify at least one user id"
        sys.exit(1)
    else:
        users = sys.argv[1:]

        for user in users:
            print "===> Fetching %s" % user
            dents = get_scrobbles(user)
			
            if not dents:
                print "ERROR: No results!"
            else:
                #save_batch(user, dents, "raw_scrobbles.json")

                for d in dents[2:]:
					time = d['date']['#text']
					artist = d['artist']['#text']
					artist_mbid = d['artist']['mbid']
					name = d['name']
					mbid = d['mbid']
					url = d['url']
					print time + "\n" + artist + "\n" + artist_mbid + "\n" + name + "\n" + mbid + "\n" + url + "\n" + "================"

