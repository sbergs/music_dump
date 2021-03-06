#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys
from mutagen.easyid3 import EasyID3
from mutagen import mutagen

def initializeDB():
  con = sqlite3.connect('music.db')
  with con:
    cur = con.cursor()
    cur.execute('''
        create table if not exists artists
          (id INTEGER PRIMARY KEY NOT NULL,
           name NVARCHAR(255) NOT NULL UNIQUE ON CONFLICT IGNORE
          )
      ''')

    cur.execute('''
        create table if not exists albums
          (id INTEGER PRIMARY KEY NOT NULL,
           name NVARCHAR(255) not null,
           artist_id integer not null,
           foreign key(artist_id) references artists(id),
           UNIQUE (name, artist_id) ON CONFLICT IGNORE
          )
      ''')

    cur.execute('''
        create table if not exists tracks
          (id INTEGER PRIMARY KEY NOT NULL,
           name NVARCHAR(255) not null,
           album_id integer not null,
           length integer not null,
           foreign key(album_id) references albums(id)
          )
      ''')
  con.commit()
  return con, cur

#create our tables
db, cur = initializeDB()

rootdir = sys.argv[1]

def save_mp3(mp3):
  cur.execute("insert into artists (name) values (?)", mp3["artist"])
  db.commit()
  cur.execute("select id from artists where name=? LIMIT 1", mp3["artist"])
  artistid = cur.fetchone()

  cur.execute("insert into albums (name,artist_id) values (?,?)", (mp3["album"][0],artistid[0]))
  db.commit()
  cur.execute("select id from albums where name=? and artist_id=? LIMIT 1", (mp3["album"][0], artistid[0]))
  albumid = cur.fetchone()

  cur.execute("insert into tracks (name, album_id, length) values (?,?,?)", (mp3["title"][0],albumid[0],mp3["length"][0]))
  db.commit()

def process_mp3(file):
  try:
    mp3 = EasyID3(file)
    save_mp3(mp3)
  except mutagen.id3.ID3NoHeaderError as e:
    print str(file) + " does not have an id3 tag"
  except sqlite3.InterfaceError as e:
    print str(e)
  except KeyError as e:
    #need to figure out sqlite quirks to really ON CONFLICT IGNORE but until then
    pass;
  except:
    print "Unexpected error:", sys.exc_info()[0]
  #

for root, subFolders, files in os.walk(rootdir):
  for filename in files:
    if filename.upper().endswith('.MP3'):
      process_mp3(os.path.join(root, filename))




