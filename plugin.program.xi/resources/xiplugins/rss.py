#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmc
import base64
from sys import argv as sys_argv
from os import path , popen , system , getenv
import feedparser
from time import mktime

#XBMC_SCRIPTSPATH = xbmc.translatePath('special://home/addons/plugin.program.xi/resources/scripts')
XBMC_SCRIPTSPATH = getenv('HOME')+'/.xbmc/addons/plugin.program.xi/resources/scripts'
XBMC_XPLSPATH = getenv('HOME')+'/.local/xpls'
LOGOURL = ''

def file_read(myfile):
  if path.exists(myfile):
    f = open(myfile, 'r')
    data = f.read()
    f.close()
    return data
  else:
    return ''

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  try:
    myetxt = mytxt.encode('utf-8')
  except:
    myetxt = mytxt
  f.write(myetxt)
  f.close()

##XDG-Parser  
def parse_xdg_file(myfile):
  mytmpcfg = {}
  for myline in file_read(myfile).split('\n'):
    mysplit = myline.split('=',1)
    if len(mysplit) == 2:
      mytmpcfg[mysplit[0]] = mysplit[1]
  #Convert URL[$e]
  if mytmpcfg.has_key('URL[$e]'):
    mytmpcfg['URL'] = mytmpcfg['URL[$e]']
  #Convert url to protocol/id
  if mytmpcfg.has_key('URL'):
    if mytmpcfg['URL'].find('://') > -1:
      myproto , myid = mytmpcfg['URL'].split('://',1)
      mytmpcfg['Proto'] , mytmpcfg['Id'] = myproto , myid.replace('@','-')
  else:
    mytmpcfg['Proto'] , mytmpcfg['Id'] = '' , ''
  return mytmpcfg

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

#Convert http://host/request to http://host
def url_to_baseurl(myurl):
  if myurl.find('://') > -1:
    myasplit = myurl.split('://',1)
    mypre = myasplit[0] + '://'
    myuripos = myasplit[1].find('/')
    if myuripos > -1:
      myouturl = mypre + myasplit[1][:myuripos]
    else:
      myouturl = mypre + myasplit[1]
    return myouturl
  return myurl
URLCACHE = {}
#Check if url gets a 404 or not - TODO: check for long files and use internal python
def url_404_check(myurl):
  global URLCACHE
  if URLCACHE.has_key(myurl):
    return URLCACHE[myurl]
  #Go-On
  myret = system_popen("wget -q '"+myurl+"' && echo -n 1")
  if myret == '1':
    mybool = True
  else:
    mybool = False
  URLCACHE[myurl] = mybool
  return mybool
  

def system_popen(mycmd):
  return popen(mycmd, 'r').read()

FAVICONDIR = getenv('HOME')+'/.thumbnails/favicons'

def get_favicon(myurl):
  myfile = get_favicon_path(myurl)
  if not path.exists(myfile):
    myfaviconurl = get_favicon_url(myurl)
    if myfaviconurl.endswith('.ico'):
      myfaviconsource = get_favicon_path(myurl,'ico')
      #Download Favicon
      system("wget -q -O '"+myfaviconsource+"' '"+ myfaviconurl +"'")
      #Get last item from ico list
      myimdata = system_popen("identify '"+myfaviconsource+"' | grep ICO | tail -1 ").rstrip('\n')
      if myimdata.find('[') > -1:
	mynum = myimdata.split('[',1)[1]
	mynum = mynum.split(']',1)[0]
	if mynum.isdigit():
	  system("convert '"+myfaviconsource+"' -blur 2x2 '"+ myfile+"'")
	  system("mv '"+myfile+"."+mynum+ "' '"+myfile+"'")
	  system("rm "+myfile+".*")
      else:
	system('convert "'+myfaviconsource+'" '+ myfile)
    else:
      system("convert '"+myfaviconurl+"' '"+ myfile +"'")
  return myfile

def get_favicon_path(myurl,mytype='png'):
  #try to parse html
  mybase = url_to_baseurl(myurl)
  myname = mybase.split('://')[1]
  myfile = FAVICONDIR + '/' + myname.replace('.','_') + '.' + mytype
  return myfile

def get_favicon_url(myurl):
  #try to parse html
  myfav = get_favicon_fromHtml(myurl)
  #Check favicon and return url
  if myfav == '':
    myfav = get_favicon_fromUrl(myurl)
    if url_404_check(myfav):
      return myfav
  #Use favicon parsed from html data
  else:
    if url_404_check(myfav):
      return myfav
  return ''

#Convert to basename and get favicon
def get_favicon_fromUrl(myurl):
  mybase = url_to_baseurl(myurl)
  myfavicon = mybase + '/favicon.ico'
  return myfavicon

def get_favicon_fromHtml(myurl):
  myline = system_popen("wget -O - -q '"+myurl+"' | grep '/favicon.ico' | grep -i 'rel=' | head -1").rstrip('\n')
  mypos = myline.lower().find('href="')
  if mypos > -1:
    myrest = myline[mypos:]
    myfavicon = myrest.split('"')[1]
    if myfavicon.startswith('/'):
      myfaviconurl = url_to_baseurl(myurl) + myfavicon
    else:
      myfaviconurl = myfavicon
    return myfaviconurl
  return ''

#Get Main Image of the parsed feed
def get_feed_image(myfeed):
  mydefimg = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/rss-feed.png'
  myimg = mydefimg
  if myfeed.has_key('feed'):
    if myfeed['feed'].has_key('image'):
      #get logo from feed
      if myfeed['feed']['image'].has_key('href'):
        myimg = myfeed['feed']['image']['href']
	if not url_404_check(myimg):
	  #Get logo from desktop-file
	  if LOGOURL != '':
	    myimg = LOGOURL
	  else:
	    #Get logo from favicon
	    myimg = get_favicon(myimg)
	    #Get default logo
	    if myimg == '':
	      myimg = mydefimg
    elif myfeed['feed'].has_key('link'):
      #myname = myfeed['feed']['link'].replace('/','').replace(':','').rstrip('\n\r') #todo escape
      myimg = get_favicon(myfeed['feed']['link'])
      ###myfavfile = get_favicon_path(myfeed['feed']['link'])
      ###myfavurl = get_favicon_url(myfeed['feed']['link'])
      ###if myfavurl
      ####print myfavurl
      ####myfavurl = url_to_baseurl(myfeed['feed']['link'])+'/favicon.ico'
      ####myfavfile = '/tmp/'+myname+'-favicon.ico'
      ###myfavpngfile = '/tmp/'+myname+'-favicon.png'
      ####system('logger -- '+'convert fav '+myfavurl+' '+myfavfile)
      ####download favicon and convert and find biggest icon
      ###if path.exists(myfavpngfile):
	###return myfavpngfile
      ###else:
	###if not path.exists(myfavfile):
	  ###system("wget -O '"+myfavfile+"' '"+myfavurl+"'")
	###system('convert '+myfavfile+' '+myfavpngfile)
	####Get bigger favicon
	###if path.exists(myfavpngfile+'.1'):
	  ###system("mv '"+myfavpngfile+"'.1 '"+myfavpngfile+"'")
	  ###return myfavpngfile
	###if path.exists(myfavpngfile):
	  ###return myfavpngfile
  return myimg

#Get Image of entry
def get_entry_image(myfeed,mypos):
  if hasattr(myfeed.entries[mypos],'enclosures'):
    myencs = len(myfeed.entries[mypos].enclosures)
    if myencs >= 1:
      myimage = myfeed.entries[mypos].enclosures[0]['href']
      if myimage.endswith('.jpg') or myimage.endswith('.png') or myimage.endswith('.gif') :
	system('logger Realimg: '+myimage)
      else:
	system('logger NonRealimg: '+myimage)
	myimage = get_feed_image(myfeed)
    else:
      myimage = get_feed_image(myfeed)
  else:
    myimage = get_feed_image(myfeed)
  #
    #myimage = str(myfeed['entries'][mypos].enclosures[1]['href'])
  #else:
    #myimage = ''
  #system('logger Nimg: '+str(myimage))
  return str(myimage)

#Walk through entries
def get_feed_entries(myfeed):
  myout = ''
  myentries = len(myfeed.entries) #-1
  mymainthumb = get_feed_image(myfeed)
  mymtype , mymedia = 'web' , ''
  for mypos in range(0,myentries):
    #mythumb = mymainthumb
    mythumb = get_entry_image(myfeed,mypos)
    try:
      mydesctext = myfeed.entries[mypos].description
      myplaintext = remove_tags(mydesctext.replace('<br>','\n'))
    except:
      mydesctext = 'Error'
      myplaintext = mydesctext
    #Check enclosure
    #TODO - enclosures ! - print myfeed.entries[mypos].enclosures[0].href
    try: 
      myenclen = len( myfeed.entries[mypos].enclosures)
    except:
      myenclen = 0
    if myenclen > 0:
      myencref = myfeed.entries[mypos].enclosures[0].href
      mymtype = 'media'
      mymedia = myencref
    #system('logger 1dasdghdhfjg -- '+str(myfeed.entries[mypos].date))
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
    mytitle = myfeed.entries[mypos].title
    #Hyperlink to real document
    try:
      myhtmlurl = myfeed.entries[mypos].link
    except:
      myhtmlurl = ''
    #Hyperlink to xbmc-plugin-conversion
    if myhtmlurl.startswith('http://www.youtube.com/watch?v='):
      myvid = myhtmlurl.split('?v=',1)[1]
      if myvid.find('&') > -1:
	myvid = myvid.split('&',1)[0]
      myuri = 'PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid='+myvid+')'
      mythumb = 'http://i3.ytimg.com/vi/'+myvid+'/default.jpg'
    elif mymedia != '':
      if mymedia.endswith('.png') or mymedia.endswith('.jpg') or mymedia.endswith('.bmb'):
	myuri = 'RunScript('+XBMC_SCRIPTSPATH+'/viewimg.py,'+mymedia+')'
      else:
	myuri = 'PlayMedia('+mymedia+')'
    else:
      mytext = '\n' + myisodate + '\n\n' + myplaintext    
      myuriopt = base64.b64encode(mytitle.encode('utf-8')) +':'+ base64.b64encode(mytext.encode('utf-8'))
      myuri = 'RunScript('+XBMC_SCRIPTSPATH+'/textbox.py,'+myuriopt+')'
    myout += myudate+'\t'+mymtype+'\t'+mytitle+'\t'+myuri+'\t'+mythumb+'\n'
  return myout , mymainthumb

def get_main_rss(myinurl):
  if myinurl.startswith('rss://'):
    
    myinurl = 'http' + myinurl[3:]
  myfeed = feedparser.parse(myinurl)
  myouttxt , mymainthumb = get_feed_entries(myfeed)
  myct = 'utf-8' # TODO - globalize and fix function with inline encoding
  if myfeed.headers.has_key('content-type'):
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

def get_full_rss(myinurl):
  myouttxt , mymainthumb = get_main_rss(myinurl)
  myout ='#icon='+mymainthumb + '\n'
  myout += myouttxt
  #try:
    #myout += myouttxt.encode('utf-8')
  #except:
  #file_write(myoutloc,myout)
  return myout

def write_main_rss(myinurl,myoutloc):
  myouttxt , mymainthumb = get_main_rss(myinurl)
  myout ='#icon='+mymainthumb + '\n'
  #try:
    #myout += myouttxt.encode('utf-8')
  #except:
  myout += myouttxt
  file_write(myoutloc,myout)

def get_xpls_id(myurl):
  myurl = myurl.lstrip('htps').lstrip(':/')
  myurl = myurl.replace('?','').replace('$','').replace('&','').replace('/','').replace('_','')
  myurl = myurl.replace('%','').replace('#','').replace(',','').replace('.','').replace(';','').replace('!','')
  return myurl
  
######
###### OLDMain
######

####def main_action(myurl,myopt='-g'):
  ####myid = get_xpls_id(myurl)
  ####myxpls = XBMC_XPLSPATH+'/'+myid+'.xpls'
  ####if myopt=='-p':
    ####return myxpls
  ####else:
    ####write_main_rss(myurl , myxpls)
    ####return myxpls

####if len(sys_argv) == 2:
  ####print main_action(sys_argv[1])
####else:
  ####print main_action(sys_argv[2],sys_argv[1]) #TODO: print xpls only mode
#####system('logger -- b')

def get_real_path(myinurl):
  if myinurl.endswith('.desktop'):
    if myinurl.lower().startswith('file://'):
      myinurl = myinurl[7:]
    myxdgcfg = parse_xdg_file(myinurl)
    if myxdgcfg.has_key('URL'):
      myinurl = myxdgcfg['URL']
    if myxdgcfg.has_key('LogoURL'):
      global LOGOURL
      LOGOURL = myxdgcfg['LogoURL']
  return myinurl
  
##
## Main
##

def main_action(myurl,myopt=''):
  myurl = get_real_path(myurl)
  myxplsdata =  get_full_rss(myurl)
  if myopt=='-d':
    return myxplsdata.encode('utf-8')
  else:
    myxpls = getenv('HOME')+'/.local/xpls/rss-'+get_xpls_id(myurl)+'.xpls'
    file_write(myxpls,myxplsdata)
    return myxpls

if len(sys_argv) == 2:
  print main_action(sys_argv[1]).rstrip('\n')
else:
  system('logger ggggg: -- '+sys_argv[1] + sys_argv[2])
  print main_action(sys_argv[2],sys_argv[1]) #TODO: check if outdir exists

#system('logger -- b')