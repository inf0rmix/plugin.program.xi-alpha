#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import base64
from sys import argv as sys_argv
from os import path , popen , system
import feedparser
from time import mktime

XBMC_SCRIPTSPATH = xbmc.translatePath('special://home/addons/plugin.program.xi/resources/scripts')

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

##HTML-Processing/Stripping

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def remove_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

##
## Feed processing
##

#Get Main Image of the parsed feed
def get_feed_image(myfeed):
  myimg = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/rss-feed.png'
  if myfeed.has_key('feed'):
    if myfeed['feed'].has_key('image'):
      #get logo from feed
      if myfeed['feed']['image'].has_key('href'):
        myimg = myfeed['feed']['image']['href']
      #Get logo from favicon
    elif myfeed['feed'].has_key('link'):
      myname = myfeed['feed']['link'].replace('/','').replace(':','').rstrip('\n\r') #todo escape
      myfavurl = myfeed['feed']['link'].rstrip('/')+'/favicon.ico'
      myfavfile = '/tmp/'+myname+'-favicon.ico'
      myfavpngfile = '/tmp/'+myname+'-favicon.png'
      system('logger -- '+'convert '+myfavurl+' '+myfavfile)
      #download favicon and convert and find biggest icon
      if path.exists(myfavpngfile):
	return myfavpngfile
      else:
	if not path.exists(myfavfile):
	  system("wget -O '"+myfavfile+"' '"+myfavurl+"'")
	system('convert '+myfavfile+' '+myfavpngfile)
	#Get bigger favicon
	if path.exists(myfavpngfile+'.1'):
	  system("mv '"+myfavpngfile+"'.1 '"+myfavpngfile+"'")
	  return myfavpngfile
	if path.exists(myfavpngfile):
	  return myfavpngfile
  return myimg

#Get Image of entry
def get_entry_image(myfeed,mypos):
  if hasattr(myfeed.entries[mypos],'enclosures'):
    myencs = len(myfeed.entries[mypos].enclosures)
    if myencs >= 1:
      myimage = myfeed.entries[mypos].enclosures[0]['href']
      if myimage.endswith('.jpg') or myimage.endswith('.png') or myimage.endswith('.gif') :
	os.system('logger Realimg: '+myimage)
      else:
	os.system('logger NonRealimg: '+myimage)
	myimage = get_feed_image(myfeed)
    else:
      myimage = get_feed_image(myfeed)
  else:
    myimage = get_feed_image(myfeed)
  #
    #myimage = str(myfeed['entries'][mypos].enclosures[1]['href'])
  #else:
    #myimage = ''
  os.system('logger Nimg: '+str(myimage))
  return str(myimage)

#Walk through entries
def get_feed_entries(myfeed):
  myout = ''
  myentries = len(myfeed.entries)
  mymainthumb = get_feed_image(myfeed)
  for mypos in range(0,myentries-1):
    #mythumb = mymainthumb
    mythumb = get_entry_image(myfeed,mypos)
    try:
      mydesctext = myfeed.entries[mypos].description
      myplaintext = remove_tags(mydesctext.replace('<br>','\n'))
    except:
      mydesctext = 'Error'
      myplaintext = mydesctext
    system('logger 1dasdghdhfjg -- '+str(myfeed.entries[mypos].date))
    if myfeed.entries[mypos].has_key('date'):
      myisodate = myfeed.entries[mypos]["date"]
      mydate = myfeed.entries[mypos]["date_parsed"]
      myudate=str(int(mktime(mydate)))
    else:
      try:
	myisodate = myfeed.entries[mypos].date
        mydate = myfeed.entries[mypos].date_parsed
        myudate=str(int(mktime(mydate)))
      except:
	myisodate , mydate , myudate = '' , '' , '1'
    system('logger 2dasdghdhfjg -- '+str(myisodate))
    mytitle = myfeed.entries[mypos].title
    mytext = '\n' + myisodate + '\n\n' + myplaintext
    myuriopt = base64.b64encode(mytitle.encode('utf-8')) +':'+ base64.b64encode(mytext.encode('utf-8'))
    myuri = 'RunScript('+XBMC_SCRIPTSPATH+'/textbox.py,'+myuriopt+')'
    #Hyperlink to real document
    myhtmlurl = myfeed.entries[mypos].link
    #Hyperlink to xbmc-plugin-conversion
    if myhtmlurl.startswith('http://www.youtube.com/watch?v='):
      myvid = myhtmlurl.split('?v=',1)[1]
      if myvid.find('&') > -1:
	myvid = myvid.split('&',1)[0]
      myuri = 'PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid='+myvid+')'
      mythumb = 'http://i3.ytimg.com/vi/'+myvid+'/default.jpg'
    myout += myudate+'\t'+'web\t'+mytitle+'\t'+myuri+'\t'+mythumb+'\n'
  return myout , mymainthumb

def get_main_rss(myinurl):
  myfeed = feedparser.parse(myinurl)
  myouttxt , mymainthumb = get_feed_entries(myfeed)
  myct = 'utf-8' # TODO - globalize and fix function with inline encoding
  if myfeed.headers['content-type'].find('charset=') > -1:
    #Strip Charset from header
    myct = myfeed.headers['content-type'].split('charset=',1)[1]
    #Strip rest of header
    if myct.find(';') > -1:
      myct = myct.split(';',1)[0]
    try:
      myouttxt = myouttxt.decode(myct)
    except:
      pass
  return myouttxt , mymainthumb

def write_main_rss(myinurl,myoutloc):
  myouttxt , mymainthumb = get_main_rss(myinurl)
  myout ='#icon='+mymainthumb + '\n'
  #try:
    #myout += myouttxt.encode('utf-8')
  #except:
  myout += myouttxt
  file_write(myoutloc,myout)

##
## Main
##

class Viewer:
    # constants
    XIURL = ''

    def __init__( self, *args, **kwargs ):
	myxpls = '/tmp/test.xpls'
	write_main_rss(sys_argv[1] , myxpls)
	self.XIURL = 'plugin://plugin.program.xi/?path='+myxpls
        # activate the text viewer window
        xbmc.executebuiltin( "PlayMedia(%s)" % ( self.XIURL ) )

if ( __name__ == "__main__" ):
    Viewer()
