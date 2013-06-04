# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon
import urllib2
from os import system , popen , path , getenv , makedirs
from sys import argv
from time import time

OURSCRIPTPATH = path.realpath(__file__)
OURBASEDIR = path.dirname(OURSCRIPTPATH)
XBMC_USERDATAPATH = xbmc.translatePath('special://profile')
DOCTYPES='pdf|doc|docx|odt|ods|odp|sdw|csv|svg|ppt|xls|ooxml|txt|rtf'
#DOCTYPES+='|html|htm|php|phtml'

#Use Config included in addon
XBMC_ADDON = xbmcaddon.Addon(id='plugin.program.xi')
USE_QWEBVIEW = XBMC_ADDON.getSetting("useQWebView")

def file_read(myfile):
  if path.exists(myfile):
    f = open(myfile, 'r')
    data = f.read()
    f.close()
    return data

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

def parse_xdg_file(myfile,isDir=False):
  mytmpcfg = {}
  for myline in file_read(myfile).split('\n'):
    mysplit = myline.split('=',1)
    if len(mysplit) == 2:
      mytmpcfg[mysplit[0]] = mysplit[1]
  if mytmpcfg.has_key('URL[$e]'):
    mytmpcfg['URL'] = mytmpcfg['URL[$e]']
    del mytmpcfg['URL[$e]']
  if not mytmpcfg.has_key('MType'):
    mytmpcfg['MType'] = ''
    if mytmpcfg.has_key('Icon'):
      if mytmpcfg['Icon'] == 'video-x-generic':
	mytmpcfg['MType'] = 'video'
      elif mytmpcfg['Icon'] == 'audio-x-generic':
	mytmpcfg['MType'] = 'audio'
      elif mytmpcfg['Icon'] == 'image-x-generic':
	mytmpcfg['MType'] = 'image'
    elif mytmpcfg.has_key('Exec'):
      mytmpcfg['MType'] = 'exec'
  #Add Comment if not set in xdf file
  if not mytmpcfg.has_key('Comment'):
    mytmpcfg['Comment'] = ''
  #Save remote playlist
  if mytmpcfg.has_key('URL'):
    if mytmpcfg['URL'].startswith('xbmcexec://'):
      mytmpcfg['MType'] = 'xbmcexec'
    else:
      mytmpcfg['URL'] = get_local_pls(mytmpcfg['URL'])
  elif mytmpcfg.has_key('Exec'):
    mytmpcfg['URL'] = 'exec://'+mytmpcfg['Exec'].replace(' ','%20')
  return mytmpcfg

#Rewrite URL/Path using xbmc Dialog and perform Action afterwards
def rewritePath(myurl,mycomment='Enter String'):
  if mycomment == '':
    mycomment = 'Enter String:'
  if myurl.find('%%XISTR%%') > -1:
    keyboard = xbmc.Keyboard('',mycomment)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      mystr = keyboard.getText()
      myurl = myurl.replace('%%XISTR%%',mystr)
  elif myurl.find('%%XINUM%%') > -1:
    dialog = xbmcgui.Dialog()
    mynum = dialog.numeric(0, mycomment)
    myurl = myurl.replace('%%XINUM%%',mynum)
  elif myurl.find('%%XIDIR%%') > -1:
    dialog = xbmcgui.Dialog()
    mypath = dialog.browse(0,'Select path...', 'files', '', False, False,'/')
    myurl = myurl.replace('%%XIDIR%%',mypath)
  return rewritePathVars(myurl)

def rewritePathVars(myurl):
  if myurl.find('%%XIYEAR%%') > -1:
    myurl = myurl.replace('%%XIYEAR%%','2013')
  if myurl.find('%%XIDAY%%') > -1:
    myurl = myurl.replace('%%XIDAY%%','01')
  if myurl.find('%%XIMONTH%%') > -1:
    myurl = myurl.replace('%%XIMONTH%%','06')
  return myurl

##
## Remote Image and Strm Cache functions
##

#Convert URL to local LiveImage-DirName
def get_local_imgdir_base(myurl):
  myurl = myurl.replace('://','_').replace('.','_')
  myurl = myurl.replace('/','_').replace('?','_')
  myurl = myurl.replace('=','_').replace('%','_')
  #RemoveDigits
  mybase = ''.join([i for i in myurl if not i.isdigit()])
  return mybase

#move all jpgs from .jpg.$NUM to -$NUM.jpg
def get_local_imgdir(myurl):
  #mybase = path.basename(myurl).replace('.','')
  mybase = get_local_imgdir_base(myurl)
  mytstamp = str(int(time()/60))
  if myurl.count('/') >= 3:
    myhost = myurl.split('/')[2].replace('.','')
    mydir = XBMC_USERDATAPATH + '/LiveImage/'+mybase
    if not path.exists(mydir):
      makedirs(mydir)
    mylimg = mydir+'/'+mytstamp+'.jpg'
    if not path.exists(mylimg):
      system("convert '"+myurl+"' '"+mylimg+"'")
    return mydir
  return '/tmp' #TODO

def get_local_gifdir(myurl):
  mybase = path.basename(myurl).replace('.','')
  mytstamp = str(int(time()/60))
  if myurl.count('/') >= 3:
    myhost = myurl.split('/')[2].replace('.','')
    mydir = XBMC_USERDATAPATH + '/LiveImage/'+mybase
    if not path.exists(mydir):
      makedirs(mydir)
    mylimg = mydir+'/'+mytstamp+'-0.jpg'
    if not path.exists(mylimg):
      system("convert '"+myurl+"' '"+mydir+'/'+mytstamp+"-%d.jpg'")
    return mydir
  return '/tmp' #TODO

def get_local_strm(myurl):
  mylurl = myurl.lower()
  if mylurl.startswith('http://') or mylurl.startswith('https://'):
    mylpath = XBMC_USERDATAPATH + '/playlists/'+get_local_name(myurl)+'.strm'
    if not os.path.exists(mylpath):
      file_write(mylpath,myurl+'\n')
    return mylpath
  return myurl

def get_local_pls(myurl):
  mylurl = myurl.lower()
  if mylurl.startswith('http://') or mylurl.startswith('https://'):
    if mylurl.endswith('.m3u') or mylurl.endswith('.pls'):
      mylpath = XBMC_USERDATAPATH + '/playlists/mixed/'+get_local_name(myurl)
      if not os.path.exists(mylpath):
	os.system('wget -O '+mylpath+' '+myurl)
      return mylpath
  return myurl

#Dialog for toggling a service using xbmc

def get_service_status(myxdgdata):
  if myxdgdata['StatusMode'] == 'pidof':
    mystat = system_popen('pidof '+myxdgdata['StatusArg'])
    if mystat[:1].isdigit():
      return True
  return False

def get_service_action(myxdgdata):
  mystat = get_service_status(myxdgdata)
  if mystat:
    mycmd = 'logger -t ficken is on kill?'
    mydialog = xbmcgui.Dialog()
    myret = mydialog.yesno('XBMC', 'Service is running - do you want to stop it ?')
    if myret:
      system(myxdgdata['StopCMD'])
    return mycmd
  else:
    mycmd = 'logger -t ficken is of start?'
    mydialog = xbmcgui.Dialog()
    myret = mydialog.yesno('XBMC', 'Service is not running - do you want to start it ?')
    if myret:
      system(myxdgdata['StartCMD'])
    return mycmd

#Scan for Action/MType automagically
def get_media_location(myurl):
  if myurl.startswith('file://'):
    myurl = myurl[7:]
    if myurl.endswith('/'):
      myurl = 'RunPlugin(plugin://plugin.program.xi/?path='+myurl.rstrip('/')+')'
  elif myurl.startswith('http://') or myurl.startswith('https://'):
    if detect_tubeurl(myurl):
      mytuberet = system_popen("youtube-dl -g '"+myurl+"'").rstrip('\n ')
      if mytuberet.startswith('http'):
	return mytuberet
    else:
      myct = get_http_contenttype(myurl)
      if myct == 'text/html':
	#ToDo: doc2slide or qwebview for html viewing
	if USE_QWEBVIEW:
	  return 'RunScript('+OURBASEDIR+'/run.py,web?'+myurl+')'
	else:
	  mydir = make_doc_slideshow(myurl)
	  if mydir.startswith('/'):
	    return 'SlideShow('+mydir+')'
      elif myct == 'text/plain':
	return 'RunScript('+OURBASEDIR+'/resources/scripts/textview.py,'+myurl+')'
      elif myct.startswith('audio/') or myct.startswith('video/'):
	return 'PlayMedia('+myurl+')'
  return myurl

def detect_tubeurl(myurl):
  TUBEHOSTS = '.youtube.|.metacafe.|.dailymotion.|.photobucket.|.depositfiles.|.facebook.|.blip.tv|.vimeo.|.myvideo.|.comedycentral.|.escapist.|.xvideos.|.soundcloud.|.infoq.|.stanfordoc.|.mtv.|.youku.|.xnxx.|.youjizz.|.pornotube.|.youporn.|.plus.google.|.arte.tv|.nba.|.justin.tv|.funnyordie.|.tweetreel.|.steam.|.ustream.|.rbmaradio.|.8tracks.|.keek.' # TODO: dynamically generate from youtube-dl
  try:
    myhost = myurl.rsplit('/')[2]
  except:
    return False
  if myhost != '':
    myhost = myhost.lower()
  else:
    return False
  for mytubehost in TUBEHOSTS.split('|'):
    if myhost.find(mytubehost) > -1:
      return True
  return False

def detect_document(myurl):
  try:
    myurlext = myurl.rsplit('.',1)[1]
  except:
    return False
  if myurlext != '':
    myurlext = myurlext.lower()
  else:
    return False
  for myext in DOCTYPES.split('|'):
    if myext == myurlext:
      return True
  return False

#Perform HEAD-Request and pass Content-Type
def get_http_contenttype(myurl):
  mysheaders = { 'User-Agent' : ' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0' }
  myhreq = urllib2.Request(myurl, None, mysheaders)
  myreq = urllib2.urlopen(myhreq)
  myhead = myreq.info()
  try:
    mytype = myhead['Content-Type']
  except:
    mytype = ''
  if mytype.find(';') > -1:
    mytype = mytype.split(';',1)[0]
  try:
    myreq.close()
  except:
    True
  return mytype

def get_media_action(myurl):
  myrealloc = get_media_location(myurl)
  if myrealloc.startswith('SlideShow('):
    return myrealloc
  elif myrealloc.startswith('PlayMedia('):
    return myrealloc
  elif myrealloc.startswith('RunScript('):
    return myrealloc
  elif myrealloc.startswith('RunPlugin('):
    return myrealloc
  elif detect_document(myrealloc):
    mydir = make_doc_slideshow(myrealloc)
    if mydir != '':
      return 'SlideShow('+mydir+')'
    else:
      return 'notification(Error doc-parsing url,'+myrealloc+')'
  else:
    return 'PlayMedia('+myrealloc+')'

def make_doc_slideshow(myurl):
  mydir = system_popen('python '+OURBASEDIR+"/resources/scripts/doc2slide '"+myurl+"'").rstrip('\n ')
  if mydir.find('\00') > -1:
    mydir = mydir.split('\00')[1]
    if mydir.startswith('/'):
      return mydir
  return ''

#Get internal action on xdg file's mtype
def get_xdg_action(myxdgdata):
  myact , mypath , mymtype = '' , myxdgdata['URL'] , myxdgdata['MType']
  if mymtype == 'audio' or mymtype == 'rss-audio':
    myact = 'ActivateWindow(10501,'+mypath+',return)'
  elif mymtype == 'video' or mymtype == 'rss-video':
    myact = 'ActivateWindow(10024,'+mypath+',return)'
  elif mymtype == 'rss-image':
    xbmc.executebuiltin('notification(test,test)')
    myact = 'ActivateWindow(10002,'+mypath+',return)'
  elif mymtype == 'radio':
    myact = 'PlayMedia('+mypath+')'
  elif mymtype == 'xbmcexec':
    myact = mypath[11:]
  elif mymtype == 'directory':
    myact = 'RunPlugin(plugin://plugin.program.xi/?path='+mypath+')'
  return myact

MTYPES_INTERNAL = {'directory':'','radio':'','rss-image':'','video':'','rss-video':'','audio':'','rss-audio':''}

def system_popen(mycmd):
  return popen(mycmd, 'r').read()

##
## EmuExec part
##

def rom_exec(myfile):
  if myfile.find('.') > -1:
    mypre , mysuf = myfile.rsplit('.',1)
    mylsuf = mysuf.lower()
    if mylsuf in [ 'adf' , 'adz' ]:
      rom_exec_amiga(myfile)
    elif mylsuf in [ 'd64' , 't64' ]:
      if mylsuf == 't64':
	rom_exec_c64_tape(myfile)
      else:
	rom_exec_c64_disk(myfile)
    elif mylsuf == 'smd':
      rom_exec_generic('gens --fs',myfile) #mednafen genesis emulation still buggy
    elif mylsuf in [ 'nes' , 'smc' , 'gb' , 'gbc' , 'gba' , 'gg' , 'sms' , 'smd' , 'lnx' , 'pce' , 'ngp' , 'msx' , 'ws' , 'wsc']:
      rom_exec_mednafen(myfile)
    elif mylsuf in [ 'msa' , 'st' ]:
      rom_exec_generic('hatari -fullscreen',myfile)
    elif mylsuf == 'mame':
      rom_exec_generic('mame',myfile)
    elif mylsuf in [ 'v64' , 'z64']:
      rom_exec_generic('mupen64plus --fullscreen',myfile)
    else:
      system("logger -- unknown system '"+myfile+"' &")


def rom_exec_getdisk_b(myfile):
  mydisknum = myfile[-5]
  myaltdisk = ''
  if mydisknum == '1':
    mydiskb = myfile[:-5]+'2'+myfile[-4:]
    if path.exists(mydiskb):
      myaltdisk=mydiskb
  elif mydisknum == 'a':
    mydiskb = myfile[:-5]+'b'+myfile[-4:]
    if path.exists(mydiskb):
      myaltdisk=mydiskb
  return myaltdisk

def rom_exec_c64_disk(myfile):
  mycmd = "x64 "
  mycmd += "-VICIIhwscale -fullscreen -8 '"
  mycmd += myfile+"' "
  myaltdisk = rom_exec_getdisk_b(myfile)
  if myaltdisk != '':
    mycmd += "-9 '"
    mycmd += myaltdisk+"' "
  system(mycmd + ' &')
  return mycmd

def rom_exec_c64_tape(myfile):
  mycmd = "x64 "
  mycmd += "-VICIIhwscale -fullscreen '"
  mycmd += myfile+"'"
  system(mycmd + ' &')
  return mycmd

def rom_exec_mednafen(myfile):
  mycmd = "optirun mednafen"
  myspecial = 'scale2x'
  myspecial = 'super2xsai'
  #myspecial = 'supereagle'
  
  mylsuf = myfile.rsplit('.',1)[1].lower()
  mymap = {'smc':'snes','gbc':'gb'}
  if mymap.has_key(mylsuf):
    mysys = mymap[mylsuf]
  else:
    mysys = mylsuf
  mycmd += ' -'+mysys+'.special '+myspecial
  mycmd += ' -'+mysys+'.stretch full '#+myspecial
  #myxres , myyres = '1440' , '900'
  #mycmd += '-'+mysys+'.xres '+myxres+' -'+mysys+'.yres '+myyres+' '
  mycmd += '-sounddriver sdl -fs 1 '
  mycmd += " '"+myfile+"'"
  system(mycmd + ' &')
  return mycmd


def rom_exec_generic(mycmd,myfile):
  mycmd += " '"+myfile+"'"
  system(mycmd + ' &')
  return mycmd


def rom_exec_amiga(myfile):
  mycmd = "padsp fs-uae --amiga-mode=A500 --fullscreen=1 --kickstart-file=/usr/lib/uae/kick.rom "
  mycmd += "--floppy-drive-0='"
  mycmd += myfile+"' "
  myaltdisk = rom_exec_getdisk_b(myfile)
  if myaltdisk != '':
    mycmd += "--floppy-drive-1='"
    mycmd += myaltdisk+"' "
  system(mycmd + ' &')
  return mycmd

##
## Main
##

def MainRun(myargcmd , myargloc):
  myargmtype = ''
  #Check for .desktop file and take internal action
  if myargloc.startswith('/') and myargloc.endswith('.desktop'):
    myargcfg = parse_xdg_file(myargloc)
    if myargcfg.has_key('Exec'):
      myargloc = rewritePath(myargcfg['Exec'],myargcfg['Comment'])
      myargcmd = 'exec'
    elif myargcfg.has_key('URL'):
      myargloc = rewritePath(myargcfg['URL'],myargcfg['Comment'])
      myargmtype = myargcfg['MType']

  if myargcmd == 'web':
    myargloc = rewritePath(myargloc,'')
    system('python '+OURBASEDIR+"/resources/scripts/qwebview view '"+myargloc+"' &")
  #elif myargcmd == 'rss':
    #xbmc.executebuiltin('RunScript('+OURBASEDIR+"/resources/scripts/rssview.py,"+myargloc+")")
    #system('python '+OURBASEDIR+"/resources/scripts/qwebview rssview '"+myargloc+"' &")
  elif myargcmd == 'anim':
    xbmc.executebuiltin('SlideShow('+get_local_gifdir(myargloc)+')')
  elif myargcmd == 'strm':
    xbmc.executebuiltin('PlayMedia('+get_local_strm(myargloc)+')')
  elif myargcmd == 'vstream':
    xbmc.executebuiltin('PlayMedia('+myargloc+')')
  elif myargcmd == 'exec':
    print 123123123
    system(myargloc+' &')
  elif myargcmd == 'service':
    system(get_service_action(myargcfg)+' &')
  elif myargcmd == 'rom':
    rom_exec(myargloc)
  elif myargcmd == 'image' or  myargcmd == 'webcam':
    xbmc.executebuiltin('SlideShow('+get_local_imgdir(myargloc)+')')
  elif myargmtype == 'html-image':
    mycimg = system_popen('python /home/inf0rmix/html-to-img.py ' + myargloc + ' ').rstrip('\n')
    xbmc.executebuiltin('SlideShow('+get_local_imgdir(mycimg)+')')
  elif myargcmd == 'scan':
    xbmc.executebuiltin(get_media_action(myargloc))
  elif myargcmd == 'doc':
    xbmc.executebuiltin(get_media_action(myargloc))
  elif myargcmd == 'rss-image':
    xbmc.executebuiltin(get_media_action(myargloc))
    xbmc.executebuiltin('Container.SetViewMode(500)')
    
  elif MTYPES_INTERNAL.has_key(myargmtype):
    xbmc.executebuiltin(get_xdg_action(myargcfg))
  else:
    True

try:
  ourargcmd , ourargloc = argv[1].split('?',1)
except:
  ourargcmd , ourargloc = '' , ''

if ourargcmd == 'parse':
  if ourargloc.startswith('file://'):
    ourargloc = ourargloc[7:]
  if ourargloc.startswith('/'):
    MainXDG = parse_xdg_file(ourargloc)
    if MainXDG['MType'] != '':
      MainRun(MainXDG['MType'] , ourargloc)
    else:
      MainRun('scan', ourargloc)
  else:
      MainRun('scan', ourargloc)
else:
  if ourargloc.startswith('http://'):
    MainRun(ourargcmd , ourargloc)
  else:
    MainRun(ourargcmd , ourargloc)
