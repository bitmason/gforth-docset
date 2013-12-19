#!/usr/local/bin/python

# Generate Dash Docset for Gforth from HTML documentation.
# Read more about Dash here: http://kapeli.com
#
# Original script from Python example suggested by http://kapeli.com/docsets:
# https://github.com/datasaur/pgdash/blob/master/pgdoc2set.py
#
# Gforth mods by Darren Stone <dstone@bitmason.com>
# Last tested on Gforth 0.7.0 documentation.
# 
# Essentially, this script creates Keyword entries for each Gforth word
# and Section entries for each topic/section in the documentation.
# As of Gforth 0.7.0, this creates 809 Keyword entries and 90 Section entries.
#
# Gforth HTML documentation is published under the GNU Free Documentation
# License 1.1.  License details are included in first page(s) of the docset.

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag 

db = sqlite3.connect('Gforth.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

docpath = 'Gforth.docset/Contents/Resources/Documents'

page = open(os.path.join(docpath,'Word-Index.html')).read()
soup = BeautifulSoup(page)

any = re.compile('.*')
for tag in soup.find_all('a', {'href':any}):
    name = tag.text.strip()
    if len(name) > 0:
        path = tag.attrs['href'].strip()
        # create entry for each link in the Word-Index.thml, skipping uninteresting links  
        if path.split('#')[0] not in ('index.html', 'Licenses.html', 'Concept-Index.html'):
            if path.split('#')[1].startswith('index'):
                entry_type = 'Keyword'
                name = name.split(' ')[0]  # each word is stripped of stack diagram 
            else:
                entry_type = 'Section'  # context for word entry (dupes ignored)
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, entry_type, path))
            print 'name: %s, type: %s, path: %s' % (name, entry_type, path)

db.commit()
db.close()
