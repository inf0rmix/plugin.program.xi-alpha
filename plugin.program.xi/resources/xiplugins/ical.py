#!/usr/bin/python
from os import path , popen , getenv
from hashlib import md5
from time import mktime
from sys import argv
import base64
import vobject

OUREVICON = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/text-vcalendar.png'
OURSCRIPTURI='RunScript(special://home/addons/plugin.program.xi/resources/scripts/textbox.py,%%XIARG%%)'
OURXPLSDIR = getenv('HOME')+'/.local/xpls'

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

def get_http_data(myurl):
  return system_popen("wget -q -O - '"+myurl+"'")

def md5sum(textToHash=None):
    return md5(textToHash).hexdigest()

def parse_ical(myindata):
  myret , myevents = {} , {}
  myret['cnt'] , myret['today'] = 0 , 0
  myret['data'] , myret['md5sum'] = '' , ''
  myisev , myadd = False , False
  myindata = myindata.replace('\r\n','\n')
  for myline in myindata.split('\n'):
    mysplit = myline.split(':',1)
    if len(mysplit) == 2:
      myret['data'] += myline + '\n'
      if mysplit[1] == 'VEVENT':
	if mysplit[0] == 'BEGIN':
	  myret['cnt'] += 1
	  myevid = str(myret['cnt'])
	  myevents[myevid] = {'DTSTART':'','DTSTOP':'','SUMMARY':'','UID':'','DESCRIPTION':''}
	  myisev = True
	elif mysplit[0] == 'END':
	  myisev = False
      elif myisev:
	myevkey = mysplit[0]
	if myevents[myevid].has_key(myevkey):
	  myevents[myevid][myevkey] = mysplit[1].replace('\t',' ')
  myret['md5sum'] = md5sum(myret['data'] )
  myret['events'] = myevents
  return myret

#Convert ICAL-DateString to Unix-Time and Time-Array
def icaldate_to_date(mystr):
  myret = {}
  myret['year'] , myret['month'] = int(mystr[0:4]) , int(mystr[4:6])
  myret['day'] , myret['hour'] = int(mystr[6:8]) , int(mystr[9:11])
  myret['min'] , myret['sec'] = int(mystr[11:13]) , int(mystr[13:15])
  #myret['today'] = myret['year'] + '/' + myret['month'] + '/' + myret['day']
  #myret['val'] = myret['today'] + ' ' + myret['hour'] +  ':' + myret['min'] +  ':' + myret['sec']
  myudate = mktime((myret['year'],myret['month'],myret['day'],myret['hour'],myret['min'],myret['sec'],0,1,0))
  myret['udate'] = str(int(myudate))
  return myret

def get_ical_descuri(myev):
  mybody = '\n' + myev['DESCRIPTION'] + '\n\n' + myev['UID'] + '\n\n'
  myarg= base64.b64encode(myev['SUMMARY'])+':'+base64.b64encode(mybody)
  myuri = OURSCRIPTURI.replace('%%XIARG%%',myarg)
  return myuri

#Convert ical-text to xpls
def dump_ical_xpls(myindata,myicon=''):
  if myicon == '':
    myout = '#icon=' + OUREVICON +'\n'
  else:
    myout = '#icon=' + myicon +'\n'
  myical = parse_ical(myindata)
  for myevent in sorted(myical['events'].keys()):
    myiev = myical['events'][myevent]
    myidate = icaldate_to_date(myiev['DTSTART'])['udate']
    myevicon = OUREVICON
    myuri = get_ical_descuri(myiev)
    myout += myidate + '\txbmc\t'+myiev['SUMMARY']+'\t'+myuri+'\t'+myevicon+'\n'
  return myout

##XDG-Parser  
def parse_xdg_file(myfile):
  mytmpcfg = {}
  for myline in file_read(myfile).split('\n'):
    mysplit = myline.split('=',1)
    if len(mysplit) == 2:
      mytmpcfg[mysplit[0]] = mysplit[1]
  #Convert url to protocol/id
  if mytmpcfg.has_key('URL'):
    if mytmpcfg['URL'].find('://') > -1:
      myproto , myid = mytmpcfg['URL'].split('://',1)
      mytmpcfg['Proto'] , mytmpcfg['Id'] = myproto , myid.replace('@','-')
  else:
    mytmpcfg['Proto'] , mytmpcfg['Id'] = '' , ''
  return mytmpcfg

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
  if argv[1] == '-p':
    myxplsfile = getenv('HOME')+'/.local/xpls/'+md5sum(argv[2])+'.xpls'
    myxplsdata = get_xpls(argv[2])
    file_write(myxplsfile,myxplsdata)
    print myxplsfile
  else:
    myxplsdata = get_xpls(argv[1])
#if len(argv) == 3:
  #myxplsfile = argv[2]
  #file_write(myxplsfile,myxplsdata)
#print 'https://www.google.com/calendar/ical/f6q2gi6tc6jpat7o8l7upjo4ag%40group.calendar.google.com/public/basic.ics'
#print icaldate_to_date('20130424T173000Z')
#arsedCal = vobject.readComponents(mydata)
#for obj in vobject.readComponents(mydata):
  #print obj.adr

#print parsedCal.vevent.dtstart.value

#print datetime.datetime(2006, 2, 16, 0, 0, tzinfo=tzutc())

