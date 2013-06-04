#!/usr/bin/python
#import xbmc , xbmcgui
from os import path , popen , getenv , system
from hashlib import md5
from time import mktime
from sys import argv
import base64
import vobject

VIEWMODE = ''
OUREVICON = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/text-vcalendar.png'
OURSCRIPTURI='RunScript(special://home/addons/plugin.program.xi/resources/scripts/textbox.py,%%XIARG%%)'
OURXPLSDIR = getenv('HOME')+'/.local/xpls'
OURTHUMBDIR = getenv('HOME')+'/.thumbnails'
OURICONBG = getenv('HOME')+'/.xbmc/addons/plugin.program.xi/resources/skins/Default/media/icon-backdrop.png'

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
  f.write(mytxt)
  f.close()

def system_popen(mycmd):
  return popen(mycmd, 'r').read()

def find_xdg_icon(myicon):
  myiconfile = ''
  mylist = system_popen('ls -1 /usr/share/icons/default.*/*/*/'+myicon+'.png')
  if mylist.find('\n') > -1:
    myiconfile = mylist.split('\n')[0]
  else:
    mylist = system_popen('ls -1 /usr/share/icons/*/*/*/'+myicon+'.png')
    if mylist.find('\n') > -1:
      myiconfile = mylist.split('\n')[0]
  return myiconfile

def get_entry_icon(myicon):
  if myicon.startswith('xdgicon://'):
    myiconname = myicon[10:]
  elif myicon != '' and myicon.find('/') == -1:
    myiconname = myicon
  #TODO: does not work for http:// !
  if myiconname != '':
    myiconfile = OURTHUMBDIR+'/'+myiconname+'.png'
    if path.exists(myiconfile):
      return myiconfile
    else:
      myrealiconfile = find_xdg_icon(myiconname)
      mygcmd = 'convert '+myrealiconfile+' -resize 128x128 - | composite -gravity center - '+OURICONBG+' '+myiconfile
      system(mygcmd)
      return myiconfile
  else:
    return myicon
      

def get_dialog_struct(myxidlgfile):
  myret , mycnt = '' , 0
  mydata = file_read(myxidlgfile)
  for myline in mydata.split('\n'):
    mysplit = myline.split('\t')
    if len(mysplit) >= 3:
      if len(mysplit) == 3:
	myicon = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/dlg-'+mysplit[0]+'.png'
      else:
	myicon = get_entry_icon(mysplit[3])
      myuri = 'dlg://'+mysplit[0]+':'+mysplit[2]
      mycnt += 1
      myret += str(mycnt)+'\tdlg'+'\t'+mysplit[1]+'\t'+myuri+'\t'+myicon+'\n'
      #myret['title'].append(mysplit[1])
      #myret['arg'].append(mysplit[2])
    elif myline.startswith('viewmode='):
      global VIEWMODE
      VIEWMODE = '&viewmode='+myline[9:]
  return myret

##
## Main Functions
##

#Parse xdg or ical file
def parse_file(myinput):
  if path.exists(myinput):
    myidata = file_read(myinput)
    mylogo = OUREVICON
    if myidata.startswith('[Desktop Entry]\n'):
      myxdata = parse_xdg_file(myinput)
      myicaldata = get_http_data(myxdata['URL'])
      #Check for logo
      if myxdata.has_key('LogoURL'):
	mylogo = myxdata['LogoURL']
      return dump_ical_xpls(myicaldata,mylogo)
    else:
      return dump_ical_xpls(myidata,mylogo)

def parse_input(myinput):
  if myinput.startswith('http://') or myinput.startswith('https://'):
    myicaldata = get_http_data(myinput)
    return dump_ical_xpls(myicaldata)
  elif myinput.startswith('/'): # TODO: file:// ??!!!
    return parse_file(myinput)

def get_xpls(myinuri):
  myxplsdata = parse_input(myinuri)
  return myxplsdata

#print parse_input('/home/inf0rmix/basic.ics')
#print 444
if len(argv) >= 2:
  myxplsdata = get_dialog_struct(argv[1])
if len(argv) == 3:
  if argv[2] == '-play':
    myxplsfile = OURXPLSDIR + '/' + path.basename(argv[1]).replace('.','-') + '.xpls'
    file_write(myxplsfile,myxplsdata)
    system("xbmc-send -a 'PlayMedia(plugin://plugin.program.xi/?path="+myxplsfile+VIEWMODE+")'")
  else:
    myxplsfile = argv[2]
    file_write(myxplsfile,myxplsdata)
else:
    myxplsfile = OURXPLSDIR + '/' + path.basename(argv[1]).replace('.','-') + '.xpls'
    file_write(myxplsfile,myxplsdata)
    system("xbmc-send -a 'PlayMedia(plugin://plugin.program.xi/?path="+myxplsfile+VIEWMODE+")'")
#print 'https://www.google.com/calendar/ical/f6q2gi6tc6jpat7o8l7upjo4ag%40group.calendar.google.com/public/basic.ics'
#print icaldate_to_date('20130424T173000Z')
#arsedCal = vobject.readComponents(mydata)
#for obj in vobject.readComponents(mydata):
  #print obj.adr

#print parsedCal.vevent.dtstart.value

#print datetime.datetime(2006, 2, 16, 0, 0, tzinfo=tzutc())

