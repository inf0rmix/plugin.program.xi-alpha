# -*- coding: utf-8 -*-
import xbmc,xbmcgui,xbmcaddon,xbmcplugin
import os
from sys import argv as sys_argv
from sys import stdout as sys_stdout
from time import time
from urllib import quote_plus
from shutil import copy as sh_copy
import CommonFunctions as common
#ln -s ~/xbmc-addons/dev/script.x.i/default.py ~/.xbmc/addons/script.x.i/default.py

#Check for pyxdg
try:
  import xdg , xdg.IconTheme
  PYXDG = True
except:
  PYXDG = False

XBMC_ADDONID = 'plugin.program.xi'
XBMC_USERDATAPATH = xbmc.translatePath('special://profile')
XBMC_ADDONPATH = xbmc.translatePath('special://home/addons/' + XBMC_ADDONID)
XBMC_ADDON = xbmcaddon.Addon(id=XBMC_ADDONID)
XBMC_MTYPES = {'anim':'','image':'','webcam':'','strm':'','vstream':'','web':'','exec':'','service':''}
XBMC_XIBASEPLUGINS = {'im':'im','rss':'rss','ical':'ical','maildir':'maildir'}
#XBMC_XDGDATAPATH = '/home/inf0rmix/xbmc-addons/xdg-menu'
OURTHUMBDIR = os.getenv('HOME')+'/.thumbnails/large'
USER_HOME = os.getenv('HOME')
USER_THUMBS = USER_HOME + '/.thumbnails/xdg'
SHOW_HIDDEN=False
#TODO?
#CWD             = xbmcaddon.Addon(__addon_id__).getAddonInfo('path')
#Get Base-Path from settings
XBMC_ADDONPATH_CFG = str(XBMC_ADDON.getSetting("xdgBaseDir"))
if XBMC_ADDONPATH_CFG != '':
  XBMC_XDGDATAPATH = XBMC_ADDONPATH_CFG.rstrip('/')
else:
  XBMC_XDGDATAPATH = XBMC_USERDATAPATH + '/xdg'

#Import Shortcuts if path does not exists
if not os.path.exists(XBMC_XDGDATAPATH):
  os.system("cp -a '"+XBMC_ADDONPATH+"/xdg' '"+XBMC_USERDATAPATH+"'")

##
##base functions
##

#Read from file
def file_read(myfile):
  if os.path.exists(myfile):
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

#Open system-command in a pipe and return data
def system_popen(cmd):
  mypipe = os.popen(cmd, 'r')
  myret = mypipe.read()
  try:
    sys_stdout.flush()
  except:
    pass
  try:
    mypipe.close()
  except:
    pass
  return myret

#Get hash of filename
def get_crc32( string ):
  try:
    myr = get_crc32_org(string)
  except:
    myr=''
    os.system('logger error on: '+string)
  return myr

#Get hash of filename
def get_crc32_org( string ):
    string = string.lower()
    bytes = bytearray(string)
    crc = 0xffffffff;
    for b in bytes:
        crc = crc ^ (b << 24)
        for i in range(8):
            if (crc & 0x80000000 ):
                crc = (crc << 1) ^ 0x04C11DB7
            else:
                crc = crc << 1;
        crc = crc & 0xFFFFFFFF
    return '%08x' % crc

##Threading
import threading
class texec(threading.Thread):
    def __init__(self, cmdline = ''):
        threading.Thread.__init__(self)
        self.cmdline = cmdline + " > /tmp/t.txt"
	self.start()
	#self.run()
    def run(self):
	try:
	  os.system(self.cmdline)
	except:
	  print 'Thread-Error:' + self.cmdline


import md5

def getname_fm_thumbnail(myfile):
  myfile = myfile.replace(' ','%20')
  file_hash = md5.new('file://'+myfile).hexdigest()
  tb_filename = USER_HOME + '/.thumbnails/large/'+file_hash + '.png'
  if os.path.exists(tb_filename):
    return file_hash + '.png'
  else:
    return ''

def get_fm_thumbnail(myfile,myforce=True):
  myfile = myfile.replace(' ','%20')
  file_hash = md5.new('file://'+myfile).hexdigest()
  #tb_filename = os.path.join(os.path.expanduser('~/.thumbnails/large'),file_hash) + '.png'
  tb_filename_large = USER_HOME + '/.thumbnails/large/'+file_hash + '.png'
  tb_filename_normal = USER_HOME + '/.thumbnails/normal/'+file_hash + '.png'
  if myforce:
    return tb_filename_large
  elif os.path.exists(tb_filename_large):
      return tb_filename_large
  elif os.path.exists(tb_filename_normal):
      return tb_filename_normal
  else:
      return ''

#Convert URL to ID
XBMC_XPLSPATH = os.getenv('HOME')+'/.local/xpls'
def get_xpls_location(myurl):
  myid = myurl.lstrip('htps').lstrip(':/')
  myid = myid.replace('?','').replace('$','').replace('&','').replace('/','').replace('_','')
  myid = myid.replace('%','').replace('#','').replace(',','').replace('.','').replace(';','').replace('!','')
  myxplspath = XBMC_XPLSPATH+'/'+myid+'.xpls'
  return myxplspath

#set cliboard contense
def cb_set(mycont):
  if mycont !='':
    mycont = mycont.replace("'","\\'")
    os.system("qdbus org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents '"+mycont+"'")

#get cliboard contense
def cb_get():
  mycont = system_popen("qdbus org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents").rstrip('\n')
  mycont = mycont.replace('\n',' ')
  return mycont

def get_local_pls(myurl):
  mylurl = myurl.lower()
  if mylurl.startswith('http://') or mylurl.startswith('https://'):
    if mylurl.endswith('.m3u') or mylurl.endswith('.pls'):
      mylpath = XBMC_USERDATAPATH + '/playlists/mixed/'+get_local_name(myurl)
      if not os.path.exists(mylpath):
	os.system('wget -O '+mylpath+' '+myurl)
      return mylpath
  return myurl

def get_local_name(myurl):
  mybase = os.path.basename(myurl)
  myhost = myurl.split('/')[2].replace(':','_').replace('.','')
  if myhost.find('@') > -1:
    myhost=myhost.rsplit('@',1)[1]
  return myhost + mybase


###
def dlg_list_to_menu(mylist):
  myret = []
  mylist = mylist.replace('\n',' ').replace('\t',' ')
  for myent in mylist.split(' '):
    myret.append(myent)
  return myret

import subprocess 

def system_subpipe(mycmd):
  p = subprocess.Popen(mycmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True).stdout
  mydata = p.read()
  print mydata
  return mydata

def dlg_cmd_to_menu(mycmd):
  
  mycmdout = system_subpipe(mycmd)
  #os.system(mycmd+' > /tmp/mylist.txt')
  #mycmdout = file_read('/tmp/mylist.txt')
  myaret , mybret = [] , []
  for myline in mycmdout.split('\n'):
    mybret.append(myline)
    mysplit = myline.split()
    if len(mysplit) >= 2:
      myaret.append(mysplit[0])
    else:
      myaret.append(myline)
  return myaret , mybret

def dlg_rewriteAction(mymode,myopt='',mycomment=''):
  myret , myvalid = '' , False
  if mymode == 'XISTR':
    if mycomment == '': mycomment = 'Enter String:'
    keyboard = xbmc.Keyboard('',mycomment)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      myret = keyboard.getText()
      myvalid = True
  elif mymode == 'XINUM':
    if mycomment == '': mycomment = 'Enter Value:'
    dialog = xbmcgui.Dialog()
    mynum = str(dialog.numeric(0, mycomment))
    if mynum.isdigit():
      myvalid = True
      myret = mynum
  elif mymode == 'XIFILE':
    dialog = xbmcgui.Dialog()
    mypath = dialog.browse(1,mycomment, 'files', '', False, False,'/')
    if mypath:
      return mypath , False
    else:
      myret = mypath
      myvalid = True
  elif mymode == 'XIDIR':
    dialog = xbmcgui.Dialog()
    mypath = dialog.browse(0,mycomment, 'files', '', False, False,'/')
    if mypath:
      return mypath , False
    else:
      myret = mypath
      myvalid = True
  elif mymode == 'XILIST':
    dialog = xbmcgui.Dialog()
    mymenu = dlg_list_to_menu(mycomment)
    myint = dialog.select('Select Action...',mymenu )
    myret = mymenu[myint]
    myvalid = True
  elif mymode == 'XICB': # TODO: is stub!!!!
    dialog = xbmcgui.Dialog()
    mymenu = dlg_list_to_menu(cb_get())
    myint = dialog.select('Select Action...',mymenu )
    myret = mymenu[myint]
    myvalid = True
  elif mymode == 'XIPIPE': #TODO: Causes 100% load
    dialog = xbmcgui.Dialog()
    dmenu_a , dmenu_b = dlg_cmd_to_menu(mycomment)
    myint = dialog.select('Select Action...',dmenu_b )
    myret = dmenu_a[myint]
    myvalid = True
  elif mymode == 'XICSV': # TODO: is stub!!!!
    dialog = xbmcgui.Dialog()
    mymenu = dlg_list_to_menu(mycomment)
    myint = dialog.select('Select Action...',mymenu )
    myret = mymenu[myint]
    myvalid = True
  return myret , myvalid

#Rewrite URL/Path using xbmc Dialog and perform Action afterwards
def dlg_rewritePathString(myurl):
  mynurl , myvalid = myurl , True
  mycnt = 0
  while myvalid and mycnt < 100:
    mynurl , myvalid = dlg_probePathString(mynurl)
    mycnt += 1
    #os.system('logger True: ' +mynurl)
  return mynurl

def dlg_probePathString(myurl):
  if myurl.find('%%') > -1:
    myurlpre , myurlsuf = myurl.split('%%',1)
    if myurlsuf.find('%%') > -1:
      myrewritedata , myrest = myurlsuf.split('%%',1)
      #split rewrite-var into parts
      mypartcnt = myrewritedata.count(':')
      mycomment , myrewriteopt = '' , ''
      if mypartcnt >= 2:
        myrewritemode , myrewriteopt , mycomment = myrewritedata.split(':',2)
      elif mypartcnt == 1:
	myrewritemode , myrewriteopt = myrewritedata.split(':',1)
      else:
	myrewritemode = myrewritedata
      mydlgret , mydlgstat = dlg_rewriteAction(myrewritemode , myrewriteopt , mycomment)
      mynewurl = myurlpre+mydlgret+myrest
      #os.system('logger newurl -- ' +mynewurl)
      return mynewurl , True
  return myurl , False
###




def get_xdg_icon_base(myicon):
  myipath = xdg.IconTheme.getIconPath(myicon,64,'default.kde4')
  if myipath == None:
    return ''
  else:
    return myipath

#Check if icon has a fully-qualified path and rewrite to local cache if necessary
def get_xdg_icon_adv(myicon):
  if myicon.startswith('file://'):
    myicon = myicon[7:]
  #todo - query special:// ???
  if myicon.startswith('/'):
    myiconname = myicon.replace('/','').replace('.','').replace(' ','_')
    myiconfile = USER_THUMBS+'/'+myiconname+'.png'
    if os.path.exists(myiconfile):
      return True , myiconname
    else:
      os.system("convert '"+ myicon + "' '" + myiconfile + "'")
      return True , myiconname
  else:
    return False , myicon

def get_xdg_icon(myicon):
  #Check fo full path
  myisfqp , mylocalname = get_xdg_icon_adv(myicon)
  #Set local name
  myithumb = USER_THUMBS+'/'+myicon+'.png'
  #Skip rest if it was localized
  if myisfqp:
    return myithumb
  #Go on
  #os.system('logger sdfsdf -- '+myithumb)
  if os.path.exists(myithumb):
    return myithumb
  else:
    myipath = get_xdg_icon_base(myicon)
    #os.system('logger get_xdg_icon -- '+myipath)
    if myipath.endswith('.svg'):
       os.system("convert '"+ myipath + "' '" + myithumb + "'")
    elif myipath.endswith('.xpm'):
      os.system("convert '"+ myipath + "' '" + myithumb + "'")
    elif myipath.endswith('.png'):
      os.system("ln -s '"+ myipath + "' '" + myithumb + "'")
    else:
      return ''
    return myithumb

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

def parse_xdg_dirdata(mydir):
  myret = {}
  if os.path.exists(mydir+'/.directory'):
    myret = parse_xdg_file(mydir+'/.directory',True)
  myret['URL'] = mydir
  myret['MType'] = 'directory'
  if not myret.has_key('Icon'):
    myret['Icon'] = 'folder-blue'
  if not myret.has_key('LogoURL'):
    myret['LogoURL'] = 'special://skin/media/DefaultFolder.png'
  return myret

#Rom-Files
def emuExec(myurl):
  mybase = os.path.basename(myurl).replace('.','')
  mytstamp = str(int(time()/60))
  if myurl.count('/') > 3:
    myhost = myurl.split('/')[2].replace('.','')
    mydir = XBMC_USERDATAPATH + '/LiveImage/'+mybase
    if not os.path.exists(mydir):
      os.makedirs(mydir)
    mylimg = mydir+'/'+mytstamp+'.jpg'
    if not os.path.exists(mylimg):
      os.system('convert '+myurl+' '+mylimg)
    return mydir
  return '/tmp' #TODO

EMUEXEC_EXT = {'mame':'mame','adf':'commodore_amiga','t64':'commodore_c64','d64':'commodore_c64','v64':'nintendo_n64','z64':'nintendo_n64','gg':'sega_gamegear','sms':'sega_mastersystem','smd':'sega_megadrive','gb':'nintendo_gb','gbc':'nintendo_gbc','gba':'nintendo_gba','nes':'nintendo_nes','smc':'nintendo_snes','pce':'pc_engine','ngp':'neogeo_pocket','lnx':'atari_lynx','msa':'atari_st','st':'atari_st','exe':'dos','ws':'wonderswan','wsc':'wonderswan_color'}

EMUEXEC_AWDIR = '/media/HDB-Var/EMU-DVD/artwork'

#EMUEXEC_CFG = {}
#EMUEXEC_CFG['sega_gamegear'] = { 'cmd':'mednafen -fs 1 ','name':'SEGA GameGear' }
#EMUEXEC_CFG['sega_mastersystem'] = { 'cmd':'mednafen -fs 1 ','name':'SEGA MasterSystem' }
#EMUEXEC_CFG['nintendo_gb'] = { 'cmd':'mednafen -fs 1 ','name':'Nintendo Gameboy' }
#EMUEXEC_CFG['nintendo_gbc'] = { 'cmd':'mednafen -fs 1 ','name':'SEGA GameGear' }
#EMUEXEC_CFG['nintendo_nes'] = { 'cmd':'mednafen -fs 1 ','name':'Nintendo NES' }
#EMUEXEC_CFG['commodore_amiga'] = { 'cmd':'padsp fs-uae --amiga-mode=A500 --kickstart-file=/usr/lib/uae/kick.rom --floppy-drive-0=','name':'Commodore Amiga' }


def find_emu_thumb(mypre,mysuf):
  mydefthumb = XBMC_ADDONPATH + '/resources/rom.png'
  if mysuf == 'mame':
    myname=os.path.basename(mypre)
    mythumb = EMUEXEC_AWDIR+'/mame/screenshots/'+myname+'.png'
    #os.system('logger mame: -- ' + mythumb)
    if os.path.exists(mythumb):
      return mythumb
  else:
    for mytype in 'boxfront' , 'screenshot' , 'cartridge':
      mythumb = EMUEXEC_AWDIR+'/by-ext/'+mysuf+'/'+mytype+'/'+mypre+'.jpg'
      if os.path.exists(mythumb):
	return mythumb
  return mydefthumb

def isEmuItem(myfile):
  myfile = myfile.lower()
  for myesuf in EMUEXEC_EXT.keys():
    if myfile.endswith('.'+myesuf):
      return True
  return False
  
#Document files
DOCVIEW_EXT = {'pdf':'doc','doc':'doc','ppt':'doc','odt':'doc','ods':'doc','odp':'doc'}

def isDocItem(myfile):
  myfile = myfile.lower()
  for myesuf in DOCVIEW_EXT.keys():
    if myfile.endswith('.'+myesuf):
      return True
  return False

#Media files
MEDIAVIEW_EXT = {'mp3':'snd','aac':'snd','ogg':'snd','mov':'vid','mpg':'vid','avi':'vid','mp4':'vid','mpeg':'vid','jpg':'img','gif':'img','png':'img'}

def isMediaItem(myfile):
  myfile = myfile.lower()
  for myesuf in MEDIAVIEW_EXT.keys():
    if myfile.endswith('.'+myesuf):
      return True
  return False

#test new addDirectory
def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(unicode(name), iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectory(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

class XIWindow(xbmcgui.WindowXML):
	selectedControlId = 0
	items_added = 0
	viewModeExt = ''
	hasparams = False
	param_path = ''
	param_viewmode = ''
	last_dlgpath = '/'

	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXML.__init__( self, *args, **kwargs )
		#xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
		#xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
		self._handle = int(sys.argv[ 1 ])
		self._path = sys.argv[ 0 ]
		self._arg = sys.argv[2]
		#self.listing = kwargs.get( "listing" )
		#self.xlogger(self._arg)
		self.xlogger('INIT - Handle is : '+str(self._handle))
		self.xlogger('INIT - Argv is : '+str(self._arg))
		#xbmc.setInfoLabel( "Container.FolderName",'ssdfsdf'  )
		if (not sys.argv[2]):
		  self.hasparams = False
		else:
		  if sys.argv[2].find('=') > -1:
		    self.hasparams = True
		    params = common.getParameters(sys.argv[2])
		    get = params.get
		
		if self.hasparams:
		  self.param_path = get("path")
		  if not self.param_path:	self.param_path = XBMC_XDGDATAPATH
		  self.param_viewmode = get("viewmode")
		  if not self.param_viewmode:	self.param_viewmode = ''
		  #try:
		    #mypath = get("path")
		  #except:
		    #mypath = ''
		#do
		if self.param_path == '':
		  self.param_path = XBMC_XDGDATAPATH
		#elif self.param_path != '':
		  #self._arg = self.param_path
		#elif self._arg == '/':
		  #self._arg = XBMC_XDGDATAPATH
		  #self.syslogger('argv is / - root')
		elif self.param_path.startswith('?'):
		  self.param_path = self.param_path[1:]
		else:
		  self._arg = XBMC_XDGDATAPATH
		  #self.param_path = XBMC_XDGDATAPATH
		self.init_list()

	def init_list(self):

		#if not os.path.isdir(self._arg):
		if self.param_path.endswith('.xpls'):
		  self.xiListMode = 'xpls'
		  self.basedir = str(self.param_path)
		elif self.param_path.endswith('.xipls.py'):
		  self.xiListMode = 'xplsplugin'
		  self.basedir = str(self.param_path)
		elif self.param_path.startswith('xiplugin://'):
		  self.basedir = str(self.param_path)
		  self.xiListMode = 'xiplugin'
		  #os.system('notify-send arhhhhgggghhhhghghhhh')
		elif os.path.isdir(self.param_path):
		  self.xiListMode = 'dir'
		  self.basedir = str(self.param_path)
		elif self.param_path != 'content_type=executable':
		  myitemdir = os.path.dirname(self.param_path)
		  myitemfile = os.path.basename(self.param_path)
		  myitem = self.getXdgItem(myitemdir,myitemfile)
		  self.syslogger('doing action on:'+self.param_path)
		  self.doItemAction(myitem)
		  self.basedir = myitemdir
		  self.xiListMode = 'item'
		else:
		  #os.system('notify-send arhhhhgggghhhhghghhhh arggh:'+str(self.param_path))
		  self.xiListMode = ''
		  self.basedir = XBMC_XDGDATAPATH
		#self.setCurrentListPosition(1)
		#test
		#mylistitem = xbmcgui.ListItem(str(self.param_path),path=str(self.param_path))#,thumbnailImage=mythumb,iconImage=mythumb)
		#xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=mylistitem,path=str(self.param_path))
		#xbmc.executebuiltin('Container.SetViewMode('+addon.getSetting('viewMode')+')')

	def addListXdgDir(self,mydir):
		for myentr in sorted(os.listdir(mydir)):
		  mydoadd = True
		  if myentr.startswith('.'):
		    if not SHOW_HIDDEN:
		      mydoadd = False
		  if mydoadd:
		    self.items_added += 1
		    myentrpath = os.path.join(mydir, myentr)
		    if myentr.endswith('.desktop'):
		      self.addItem(self.getXdgItem(mydir, myentr))
		    elif isMediaItem(myentr):
		      self.addItem(self.getMediaItem(mydir, myentr))
		    elif isEmuItem(myentr):
		      #self.syslogger('emuitem'+myentr)
		      self.addItem(self.getEmuItem(mydir, myentr))
		    elif isDocItem(myentr):
		      self.addItem(self.getDocItem(mydir, myentr))
		    elif myentr.endswith('.xipls.py'):
		      self.addItem(self.getPluginItem(mydir, myentr))
		    elif myentr.endswith('.xidlg'):
		      self.addItem(self.getDialogItem(mydir, myentr))
		    elif myentr.endswith('.dlg'):
		      self.addItem(self.getDialoglistItem(mydir, myentr))
		    elif myentr.endswith('.xpls'):
		      self.addItem(self.getXplsItem(mydir, myentr))
		    elif myentr.endswith('.ipls'):
		      self.addItem(self.getIplsItem(mydir, myentr))
		    elif os.path.isdir(myentrpath):
		      myitem = self.getDirItem(myentr,myentrpath)
		      #myurl = sys_argv[0]+''+sys_argv[2]
		      #xbmcplugin.addDirectoryItem(handle=self._handle, url=myurl ,listitem=myitem,isFolder=True)
		      self.addItem(myitem)
		      xbmcplugin.setResolvedUrl(handle=self._handle, succeeded=True, listitem=myitem)
		      #liz = self.getDirItem(myentr,myentrpath)
		      #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=myentrpath,listitem=liz,isFolder=True) 
		      #self.addItem(okitem)

	def getEmuItem(self,myedir,myefile):
		#try to get thumbnail
		myrpre , myrsuf = myefile.rsplit('.',1)
		myrlsuf = myrsuf.lower()
		#prepare Emu-Information
		myepath = myedir+'/'+myefile
		mycemuname = EMUEXEC_EXT[myrlsuf]
		#mycemu = EMUEXEC_CFG[mycemuname]
		#myromcmd = mycemu['cmd']+" '"+myedir+'/'+myefile+"'"
		#Todo: Emu Thumbnail facility?
		
		#mythumb = '/media/HDB-Var/EMU-DVD/artwork/'+mycemuname+'/cartridge/'+myrpre+'.jpg'
		#mythumb = '/media/HDB-Var/EMU-DVD/artwork/'+mycemuname+'/boxfront/'+myrpre+'.jpg'
		#if not os.path.exists(mythumb):
		  #mythumb = XBMC_ADDONPATH + '/resources/icons/rom-'+myrlsuf+'.png'
		  #if not os.path.exists(mythumb):
		    #mythumb = XBMC_ADDONPATH + '/resources/rom.png'
		    
		#Try to get icons from emuexec-thumbnailer
		mythumbname = getname_fm_thumbnail(myedir+'/'+myefile)
		if mythumbname != '':
		  mythumb = USER_HOME + '/.thumbnails/large/'+mythumbname
		  myicon = USER_HOME + '/.thumbnails/normal/'+mythumbname
		else:
		  mythumb = find_emu_thumb(myrpre,myrlsuf)
		  myicon = mythumb
		#mythumb = ''
		#Format Title
		mytitle = myefile.replace(' (','_').replace(')','')
		mytitle = mytitle.replace(' [!]','')
		if mytitle.find('.') > -1:
		  mytitlepre , mysuf = mytitle.rsplit('.',1)
		  mytitle = mytitlepre+' - '+mysuf.upper()
		#Generate ListItem
		mylistitem = xbmcgui.ListItem(mytitle,thumbnailImage=mythumb,iconImage=myicon)
		myuri=self.getItemAction(myepath,'rom',myepath)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', myedir+'/'+myefile)
		mylistitem.setProperty('IsPlayable', 'false')
		#mylistitem.setProperty('Folder', 'true')
		mylistitem.setProperty('MType', 'rom')
		#mylistitem.setProperty('RomCMD', myromcmd)
		mylistitem.addContextMenuItems([('Context', 'XBMC.RunScript()')], replaceItems=False)
		#self.addItem(mylistitem)
		return mylistitem

	def getXdgItem(self,myxdgdir,myxdgfile):
		mycm = []
		mycm.append( ( "Search on Title", 'notification(test,test)' ) )
		mycm.append( ( "Search on Titleasd", 'notification(test,test)' ) )
		myttitle = myxdgfile[:-8]
		myxdgpath = myxdgdir+'/'+myxdgfile
		#Parse data of xdg-file and select icon
		mydata = parse_xdg_file(myxdgdir+'/'+myxdgfile)
		if mydata.has_key('LogoURL'):
		  mythumb = mydata['LogoURL']
		elif mydata.has_key('Icon'):
		  mythumb = get_xdg_icon(mydata['Icon'])
		  if mythumb == '':
		    mythumb = get_xdg_icon('application-x-executable')
		else:
		  mythumb = 'special://skin/media/DefaultFile.png'
		#os.system('logger -- thumb:'+ mythumb+get_crc32_org(mythumb))
		#if mythumb.endswith('.svg'):
		  #mythumb = get_xdg_icon('application-x-executable')
		#if mythumb.endswith('.xpm'):
		  #mythumb = get_xdg_icon('application-x-executable')
		if mythumb == '':
		  mythumb = 'special://skin/media/DefaultFile.png'
		#Generate ListItem
		if mydata.has_key('URL'):
		  mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		  myuri=self.getItemAction(mydata['URL'],mydata['MType'],myxdgpath)
		  mylistitem.setProperty('path', myuri)
		  mylistitem.setProperty('ipath', myxdgdir+'/'+myxdgfile)
		  mylistitem.setProperty('XDGurl', mydata['URL'])
		  mylistitem.setProperty('XDGpath', myxdgpath)
		  mylistitem.setProperty('IsPlayable', 'false')
		  mylistitem.setProperty('XDGComment', mydata['Comment'])
		  mylistitem.setProperty('MType', mydata['MType'])
		  mylistitem.addContextMenuItems(mycm, replaceItems=True)
		else:
		  self.syslogger(' no URL for '+myxdgpath)
		  mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		  mylistitem.setProperty('path', '')
		  mylistitem.setProperty('XDGpath', myxdgpath)
		  mylistitem.setProperty('IsPlayable', 'false')
		  mylistitem.setProperty('XDGComment', 'Error getting URL for '+myxdgpath)
		  mylistitem.setProperty('MType', '')
		return mylistitem

	def getDirItem(self,myttitle,mypath):
		myxdgdirdata = parse_xdg_dirdata(mypath)
		if myxdgdirdata.has_key('LogoURL'):
		  myxdgthumb = myxdgdirdata['LogoURL']
		else:
		  myxdgthumb = xdg.IconTheme.getIconPath(myxdgdirdata['Icon'],64,'default.kde4')
		if myxdgdirdata.has_key('viewmode'):
		  myparams = '&viewmode='+myxdgdirdata['viewmode']
		else:
		  myparams = ''
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=myxdgthumb,iconImage=myxdgthumb)
		self.syslogger(mypath)
		myuri=self.getItemAction(mypath,'directory',mypath,myparams)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', mypath)
		mylistitem.setProperty('Folder', 'true')
		mylistitem.setProperty('MType', 'directory')
		mylistitem.setProperty('IsPlayable', 'false')
		mylistitem.addContextMenuItems([('Context', 'XBMC.RunScript()')], replaceItems=False)
		u = 'plugin://plugin.program.xi/?path='+mypath
		#xbmcplugin.addDirectoryItem(handle=self._handle, url=u ,listitem=mylistitem,isFolder=True)
		#xbmcplugin.setResolvedUrl(int(self._handle), True, mylistitem)
		return mylistitem

	def getDocItem(self,mypdir,mypfile):
		myttitle=mypfile
		myuri = 'RunScript('+XBMC_ADDONPATH+'/run.py,doc?'+mypdir+'/'+mypfile+')'
		myxdgthumbnail = get_fm_thumbnail(mypdir+'/'+mypfile)
		if myxdgthumbnail != '':
		  mythumb = myxdgthumbnail
		else:
		  mythumb='special://skin/media/DefaultAddonSubtitles.png'
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', mypdir+'/'+mypfile)
		mylistitem.setProperty('MType', 'doc')
		mylistitem.setProperty('Folder', 'false')
		return mylistitem

	def getMediaItem(self,mypdir,mypfile):
		myttitle=mypfile
		myext = mypfile.rsplit('.',1)[1]
		myuri = 'PlayMedia('+mypdir+'/'+mypfile+')'
		myxdgthumbnail = get_fm_thumbnail(mypdir+'/'+mypfile)
		if myxdgthumbnail != '':
		  mythumb = myxdgthumbnail
		else:
		  mythumb='special://skin/media/DefaultAddonSubtitles.png'
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', mypdir+'/'+mypfile)
		mylistitem.setProperty('MType', 'generic')
		mylistitem.setProperty('Folder', 'false')
		return mylistitem

	def getPluginItemIcon(self,mypdir,mypfile):
		myname = mypfile[:-8] #Remove .xipls.py
		#Todo - only works for real xdg-names
		myiconfile = USER_THUMBS+'/'+myname+'.png'
		if os.path.exists(myiconfile):
		  #os.system("logger cpa '"+myiconfile+"'")
		  return myiconfile
		else:
		  mypicon = ''
		  mypluginsrc = file_read(mypdir+'/'+mypfile)
		  mypisplit = mypluginsrc.split('#icon:',1)
		  if len(mypisplit) == 2:
		    mypiconstr=mypisplit[1].split('\n',1)[0]
		    mypiconfile = get_xdg_icon(mypiconstr)
		    if os.path.exists(mypiconfile):
		      os.system("cp '"+mypiconfile+"' '"+myiconfile+"'")
		      return myiconfile
		  return ''

	def getPluginItem(self,mypdir,mypfile):
		myttitle=mypfile[:-5]
		myuri = 'PlayMedia(plugin://'+XBMC_ADDONID+'/?path='+mypdir+'/'+mypfile+')'
		mythumb = self.getPluginItemIcon(mypdir,mypfile)
		if mythumb == '':
		  mythumb='special://skin/media/DefaultProgram.png'
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', mypdir+'/'+mypfile)
		mylistitem.setProperty('MType', 'xplsplugin')
		mylistitem.setProperty('Folder', 'false')
		return mylistitem



	def getDialogItemThumb(self,mypdir,mypfile):
		mythumb = get_fm_thumbnail(mypdir+'/'+mypfile,True)
		if not os.path.exists(mythumb):
		  myxidlgdata = file_read(mypdir+'/'+mypfile)
		  #Get icon variable
		  mysplit = myxidlgdata.split('\n$icon=')
		  if len(mysplit) >= 2:
		    myicon = mysplit[1].split('\n')[0]
		    #TODO make it more flexible
		    if myicon.startswith('http://') or myicon.startswith('https://'):
		      os.system("wget -q -O - '"+myicon+"' | convert - "+mythumb)
		    elif myicon.startswith('file://'):
		      os.system("convert '"+myicon[7:]+"' "+mythumb)
		    elif myicon.startswith('/'):
		      os.system("convert '"+myicon+"' "+mythumb)
		    else:
		      myiconfile = xdg.IconTheme.getIconPath(myicon,256,'default.kde4')
		      if not os.path.exists(myiconfile):
			myiconfile = xdg.IconTheme.getIconPath(myicon,128,'default.kde4')
			if not os.path.exists(myiconfile):
			  myiconfile = xdg.IconTheme.getIconPath(myicon,64,'default.kde4')
			  if not os.path.exists(myiconfile):
			    myiconfile=xbmc.translatePath('special://skin/media')+'/DefaultProgram.png'
		      #os.system('logger icon '+myiconfile+' '+mythumb)
		      os.system('convert '+myiconfile+' '+mythumb)
		  else:
		    myiconfile=xbmc.translatePath('special://skin/media')+'/DefaultProgram.png'
		    #os.system('logger icon '+myiconfile+' '+mythumb)
		    os.system('ln -s '+myiconfile+' '+mythumb)
		    return myiconfile
		return mythumb

	def getDialogItem(self,mypdir,mypfile):
		myttitle=mypfile[:-6]
		myuri = 'RunScript('+XBMC_ADDONPATH+'/xidlg.py,'+mypdir+'/'+mypfile+')'
		mythumb=self.getDialogItemThumb(mypdir,mypfile)
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', mypdir+'/'+mypfile)
		mylistitem.setProperty('MType', 'xbmcbuiltin')
		mylistitem.setProperty('Folder', 'true')
		return mylistitem

	def getDialoglistItem(self,mypdir,mypfile):
		myttitle=mypfile[:-4]
		myuri = 'RunScript('+XBMC_ADDONPATH+'/dlg.py,'+mypdir+'/'+mypfile+')'
		mythumb=self.getDialogItemThumb(mypdir,mypfile)
		#mythumb=xbmc.translatePath('special://skin/media')+'/DefaultProgram.png'
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', mypdir+'/'+mypfile)
		mylistitem.setProperty('MType', 'xbmcbuiltin')
		mylistitem.setProperty('Folder', 'true')
		return mylistitem

	def getXplsItemThumb(self,mypdir,mypfile):
		#Try to get icon from $HOME/.thumbnails/large
		mylthumb = get_fm_thumbnail(mypdir+'/'+mypfile,True)
		if os.path.exists(mylthumb):
		  return mylthumb
		#Try to parse xpls file for icon=
		myxpls = file_read(mypdir+'/'+mypfile).replace('\r','')
		for myline in myxpls.split('\n'):
		  if myline.startswith('#icon='):
		    mythumb=myline[6:]
		    #TODO: check for https:// or file:// and convert to local thumbnail
		    if mythumb.startswith('special://'):
		      myrealthumb = xbmc.translatePath(mythumb)
		      os.system("convert '"+myrealthumb+"' '"+mylthumb+"'")
		      return mylthumb
		    elif mythumb.startswith('/'):
		      os.system("convert '"+mythumb+"' '"+mylthumb+"'")
		      return mylthumb
		    elif mythumb.startswith('http://'):
		      os.system("convert '"+mythumb+"' '"+mylthumb+"'")
		      return mylthumb
		return 'special://skin/media/DefaultProgram.png'

	def getXplsItem(self,mypdir,mypfile):
		myttitle=mypfile[:-5]
		#myuri = 'PlayMedia('+XBMC_ADDONPATH+'/xidlg.py,'+mypdir+'/'+mypfile+')'
		myiuri = mypdir+'/'+mypfile
		myuri = 'PlayMedia(plugin://'+XBMC_ADDONID+'/?path='+myiuri
		#Get View-Mode
		myuri += self.getXplsItemViewmode(myiuri,'viewmode')
		myuri += ')'
		#mythumb=self.getDialogItemThumb(mypdir,mypfile)
		mythumb=self.getXplsItemThumb(mypdir,mypfile)
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', myiuri)
		mylistitem.setProperty('MType', 'xbmcbuiltin')
		mylistitem.setProperty('Folder', 'true')
		return mylistitem

	def getXplsItemViewmode(self,mypdir,mypfile):
		myviewmode = self.getVarFromFile(mypdir+'/'+mypfile,'viewmode','50')
		if myviewmode != '':
		  return '&viewmode='+myviewmode
		return ''

	def getIplsItem(self,mypdir,mypfile):
		myttitle=mypfile[:-5]
		#myuri = 'PlayMedia('+XBMC_ADDONPATH+'/xidlg.py,'+mypdir+'/'+mypfile+')'
		myiuri = mypdir+'/'+mypfile
		myiplsdir = XBMC_USERDATAPATH+'/DocumentViewer/ipls-'+myttitle
		myuri = myiplsdir+'.zip'#+myiuri
		##Get View-Mode
		#myuri += self.getXplsItemViewmode(myiuri,'viewmode')
		#myuri += ')'
		#mythumb=self.getDialogItemThumb(mypdir,mypfile)
		mythumb=self.getXplsItemThumb(mypdir,mypfile)
		#mythumb='special://skin/media/DefaultProgram.png'
		mylistitem = xbmcgui.ListItem(myttitle,thumbnailImage=mythumb,iconImage=mythumb)
		mylistitem.setProperty('path', myuri)
		mylistitem.setProperty('ipath', myiuri)
		mylistitem.setProperty('MType', 'ipls')
		mylistitem.setProperty('Folder', 'true')
		return mylistitem

	def getVarFromFile(self,mydfile,myvar,mydef=''):
		try:
		  myphandle = open(mypdir+'/'+mypfile)
		except:
		  return mydef
		mydorun = True
		while mydorun:
		  try:
		    myline = myphandle.readline()
		  except:
		    mydorun = False
		  if mydorun:
		    if myline.find('\t') > -1:
		      mydorun = False
		    else:
		      if myline.startswith(myvar+'='):
			myvsplit=myline.split('=',1)
			return myvsplit[1]
		return mydef

	def getCDItem(self):
		mylistitem = xbmcgui.ListItem('..')
		#mylistitem.setProperty('path', myuri)
		#mylistitem.setProperty('ipath', myiuri)
		#mylistitem.setProperty('MType', 'xbmcbuiltin')
		#mylistitem.setProperty('Folder', 'true')
		return mylistitem

	def addListXPLSFile(self,myxplsfile):
		mydata = file_read(myxplsfile)
		self.addListXPLS(mydata)

	def addListXIPipe(self,myxplsplugin):
		myplug = myxplsplugin[11:]
		if myplug.find('/') > -1:
		  myplug , myarg = myplug.split('/',1)
		else:
		  myarg = ''
		myplugfile = XBMC_ADDONPATH + '/resources/xiplugins/'+myplug+'.py'
		#os.system('logger sdf -- '+"python '"+myplugfile+"' '"+myarg+"'")
		myfiledata = system_popen("python '"+myplugfile+"' -p '"+myarg+"'").rstrip('\n')
		self.addListXPLSFile(myfiledata)

	def addListXPLSPipe(self,myxplsplugin):
		mydata = system_popen("python '"+myxplsplugin+"'")
		self.addListXPLS(mydata)

	def addListXPLS(self,mydata):
		#myttitle=mypfile[:-5]
		for myline in mydata.split('\n'):
		  #myisplit = myline.split('\00')
		  myisplit = myline.split('\t')
		  if len(myisplit) == 5:
		    mytime=myisplit[0]
		    mymode=myisplit[1]
		    mytitle=myisplit[2]
		    myuri = myisplit[3]
		    mythumb=myisplit[4]
		    mylistitem = xbmcgui.ListItem(mytitle,thumbnailImage=mythumb,iconImage=mythumb)
		    mylistitem.setProperty('path', myuri)
		    mylistitem.setProperty('ipath', myuri)
		    mylistitem.setProperty('MType', '')
		    mylistitem.setProperty('Folder', 'False')
		    self.addItem(mylistitem)
		    self.items_added += 1
		  elif myline.startswith('$viewmode='):
		    self.viewModeExt = myline.split('=',1)[1]

	def onInit(self):
		#self.init_list()
		mysuccess = False
		if self.param_viewmode == '':
		  myviewmode = str(XBMC_ADDON.getSetting("viewMode"))
		else:
		  myviewmode = self.param_viewmode
		xbmc.executebuiltin('Container.SetViewMode('+myviewmode+')')
		if self.xiListMode == 'xpls':
		  self.xlogger('xpls '+self.basedir)
		  self.addListXPLSFile(self.basedir)
		  mysuccess = False
		  #xbmcplugin.endOfDirectory( handle=int( self._handle ), succeeded=False , cacheToDisc=True)
		elif self.xiListMode == 'xiplugin':
		  self.xlogger('xiplugin '+self.basedir)
		  self.addListXIPipe(self.basedir)
		elif self.xiListMode == 'xplsplugin':
		  self.xlogger('xplsplugin '+self.basedir)
		  self.addListXPLSPipe(self.basedir)
		elif self.xiListMode == 'item':
		  self.xlogger('xdefdir '+XBMC_XDGDATAPATH)
		  self.addListXdgDir(XBMC_XDGDATAPATH)
		elif self.basedir != '':
		  self.xlogger('xdir '+self.basedir)
		  self.addListXdgDir(self.basedir)
		else:
		  mysuccess = False
		  #xbmcplugin.endOfDirectory( handle=int( self._handle ), succeeded=False , cacheToDisc=True)
		  #xbmcplugin.endOfDirectory( handle=int( self._handle ), succeeded=False , cacheToDisc=False)
		mysuccess = True
		xbmcplugin.endOfDirectory( int( self._handle ), succeeded=mysuccess, updateListing=False , cacheToDisc=True)
		xbmc.executebuiltin('setfocus('+str(myviewmode)+')')
		#self.setFocus(51)
		#self.setFocus(500)
		#os.system('notify-send endOfDirectory ')
		#xbmc.executebuiltin("Container.Refresh("+self.basedir+')')
		#pass
		#if self.viewModeExt != '':
		  #print 131231231231,self.viewModeExt
		  #xbmc.executebuiltin('Container.SetViewMode('+self.viewModeExt+')')
		#else:
		  #xbmc.executebuiltin('Container.SetViewMode('+myviewmode+')')

	def doClearList(self):
		mycditem = self.getListItem(0)
		self.clearList()
		self.addItem(mycditem)

	def onAction(self,myact=''):
		#try:
		  #self.syslogger(' running action '+str(myact))
		  #self.syslogger(' running actionid '+str(myact.getId()))
		#except:
		  #True
		if myact == 10 or myact == 92 :
		  if self.basedir == XBMC_XDGDATAPATH:
		    xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
		  else:
		    self.close()
		elif myact == 117 :
		  self.showContextMenu()
		elif myact == 122 :
		  #os.system('ubeep')
		  self.doClearList()
		  xbmcplugin.endOfDirectory( int( self._handle ), succeeded=False, updateListing=False , cacheToDisc=True)
		  self.init_list()
		  self.onInit()
		  self.syslogger('xwarning: PlayMedia(plugin://plugin.program.xi/?'+self._arg)
		  xbmc.executebuiltin('PlayMedia(plugin://plugin.program.xi/?'+self._arg)
		  #if self.getListSize() == 1:
		    #self.init_list()
		    #self.onInit()
		  self.syslogger('ficken2')
		  os.system('notify-send gfdfg '+str(self.getListSize()))
		else:
		  myactid = myact.getId()
		  if myactid == 107:
		    True
		  elif myactid >= 1 or myactid <= 4:
		    self.syslogger(' unknown action '+str(myactid))
		    self.selectedItem = self.getCurrentListPosition()
		  #myct = self.getControl(myact)
		  #self.syslogger(' 2numert -- '+str(self.getSelectedPosition()))
		#pass
	
	def onClick(self,myCtrlId):
		if myCtrlId == 50 or myCtrlId == 51 or myCtrlId == 500:
		  pos = self.getCurrentListPosition()
		  if pos == 0:
		    if self.basedir == XBMC_XDGDATAPATH:
		      xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
		    else:
		      self.close()
		  self.syslogger('asdpos '+str(pos))
		  self.selectedItem = pos
		  selItem = self.getListItem(pos)
		  self.doItemAction(selItem)
		elif myCtrlId == 2:
		  self.toggleViewMode()
		  self.syslogger('view mode')

	def doDialogAction(self,mycmode,mycarg):
		#Perform action
		if mycmode == 'run':
		  #xbmc.executebuiltin('Notification(Executing,'+mycarg+')')
		  os.system(mycarg+' &')
		elif mycmode == 'int':
		  #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
		  xbmc.executebuiltin(mycarg)
		elif mycmode == 'cli':
		  #myclistr = mycarg.replace(' ','%20')
		  #self.syslogger('cliviewer')
		  xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/cliview.py,'+mycarg+')')
		elif mycmode == 'cmd':
		  #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
		  mydialog = xbmcgui.Dialog()
		  myret = system_popen(mycarg)
		  mydialog.ok('Output:',myret)
		elif mycmode == 'cat':
		  #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
		  xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,cat:'+mycarg+')')
		elif mycmode == 'tac':
		  #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
		  xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,tac:'+mycarg+')')
		elif mycmode == 'tail':
		  #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
		  xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,tail:'+mycarg+')')
		elif mycmode == 'head':
		  #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
		  xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,head:'+mycarg+')')

	def doItemAction(self,myItemObject):
		mycpath = myItemObject.getProperty('path')
		myipath = myItemObject.getProperty('ipath')
		myxdgurl = myItemObject.getProperty('XDGurl')
		myxdgpath = myItemObject.getProperty('XDGpath')
		mymtype = myItemObject.getProperty('MType')
		self.syslogger('doitemaction on '+mycpath+' mtype: '+mymtype)
		#if mymtype == 'xplsplugin':
		  #mypaction = myItemObject.getProperty('paction')
		  #xbmc.executebuiltin(mypaction)
		  #xbmc.executebuiltin(mycpath)
		#el
		if mycpath.startswith('dlg://'):
		  #mydlguri=dlg_rewritePathString(mycpath[6:])
		  #mydlgcmd , mydlgarg = mydlguri.split(':',1)
		  #self.doDialogAction(mydlgcmd,mydlgarg)
		  #os.system('ls')
		  ##mydlgexecpath=
		  ##xbmc.executebuiltin(mycpath)
		  xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/dlgexec.py,'+mycpath+')')
		elif XBMC_XIBASEPLUGINS.has_key(mymtype):
		  myxplspath = get_xpls_location(myxdgpath)
		  myxiplugin = XBMC_ADDONPATH+'/resources/xiplugins/'+mymtype+".py"
		  self.syslogger('cur-xpls:'+myxplspath)
		  if not os.path.exists(myxplspath):
		    self.syslogger('generating xpls:'+myxdgpath)
		    os.system("python '"+myxiplugin+"' '"+myxdgpath+"' '"+myxplspath+"'")
		  else:
		    if os.path.exists(myxplspath+'.rebuild'):
		      self.syslogger('rebuilding xpls:'+myxdgpath)
		      os.system("python '"+myxiplugin+"' '"+myxdgpath+"' '"+myxplspath+"' &")
		      os.system('rm '+myxplspath+'.rebuild')
		  xbmc.executebuiltin(mycpath)
		elif mymtype == 'rss-image':
		  xbmc.executebuiltin(mycpath)
		  xbmc.executebuiltin('Container.SetViewMode(500)')
		  #xbmcplugin.setResolvedUrl()
		elif mymtype == 'ipls':
		  if not os.path.exists(mycpath):
		    os.system("python /home/inf0rmix/ipls-fetch.py '"+myipath+"' '"+mycpath+"'")
		  xbmc.executebuiltin('SlideShow('+mycpath+')')
		elif mycpath != '':
		  self.syslogger('doItemAction with '+mycpath)
		  if mycpath.find('%%') > -1:
		    mycpath = dlg_rewritePathString(mycpath)
		  xbmc.executebuiltin(mycpath)
		  #xbmcplugin.setResolvedUrl()

	def getItemAction(self,mypath,mymtype,xdgpath,myparams=''):
		#self.syslogger('getItemAction with '+mypath+' - '+mymtype+' - '+xdgpath)
		if mymtype == 'audio' or mymtype == 'rss-audio':
		  myactret = 'ActivateWindow(10501,'+mypath+',return)'
		elif mymtype == 'video' or mymtype == 'rss-video':
		  myactret = 'ActivateWindow(10024,'+mypath+',return)'
		elif mymtype == 'rss-image':
		  myactret = 'ActivateWindow(10002,'+mypath+',return)'
		elif mymtype == 'xiplugin':
		  myactret = 'RunScript('+XBMC_ADDONPATH+'/resources/scripts/xiplugin.py,'+mypath+')'
		elif mymtype == 'radio':
		  myactret = 'PlayMedia('+mypath+')'
		elif mymtype == 'media':
		  myactret = mypath
		elif mymtype == 'web':
		  myactret = 'RunScript('+XBMC_ADDONPATH+'/run.py,web?'+mypath+')'
		  #myactret = 'RunScript('+XBMC_ADDONPATH+'/resources/scripts/qwebview.py,'+mypath+')'
		elif mymtype == 'xbmcexec':
		  myactret = mypath[11:]
		#elif mymtype == 'exec':
		  #myactret = mypath[11:]
		elif mymtype == 'directory':
		  #myactret = 'RunPlugin(plugin://'+XBMC_ADDONID+'/?'+mypath+')'
		  myactret = 'PlayMedia(plugin://'+XBMC_ADDONID+'/?path='+mypath+myparams+',isdir)'
		  #os.system('notify-send here')
		  #myactret = 'RunPlugin(plugin://'+XBMC_ADDONID+'/?path='+mypath+myparams+')'
		elif mymtype == 'rom':
		  myactret = 'RunScript('+XBMC_ADDONPATH+'/run.py,rom?'+mypath+')'
		#Get xpls-Location from xiplugin
		elif XBMC_XIBASEPLUGINS.has_key(mymtype):
		  ##Get from Plugin (deactivated)
		  #OLD
		  ##myxiplugin = XBMC_ADDONPATH+'/resources/xiplugins/'+mymtype+".py"
		  ###myxplspath = system_popen("python '"+myxiplugin+"' -p '"+xdgpath+"'").rstrip('\n')
		  ##myxplspath = get_xpls_location(xdgpath)
		  ##myactret = 'PlayMedia(plugin://'+XBMC_ADDONID+'/?path='+myxplspath+')'
		  #New
		  myxiplugin = XBMC_ADDONPATH+'/resources/xiplugins/'+mymtype+".py"
		  myxplspath = get_xpls_location(xdgpath)
		  myxipluginpath = 'xiplugin://'+mymtype+'/'+xdgpath
		  myactret = 'PlayMedia(plugin://'+XBMC_ADDONID+'/?path='+myxipluginpath+',isdir)'
		elif XBMC_MTYPES.has_key(mymtype):
		  myactret = 'RunScript('+XBMC_ADDONPATH+'/run.py,'+mymtype+'?'+xdgpath+')'
		else:
		  myactret = 'RunScript('+XBMC_ADDONPATH+'/run.py,scan?'+xdgpath+')'
		return myactret

	def onFocus(self,mycid=0):
		#os.system('logger dfg -- '+str(myact))
		self.selectedItem = self.getCurrentListPosition()
		pass

	def toggleViewMode(self):
		mymode = str(XBMC_ADDON.getSetting("viewMode"))
		#TODO - this might be an evil hack
		if mymode == '50':
		  mynextmode = '51'
		elif mymode == '51':
		  mynextmode = '500'
		else:
		  mynextmode = '50'
		XBMC_ADDON.setSetting("viewMode",mynextmode)
		xbmc.executebuiltin('Container.SetViewMode('+mynextmode+')')

	def showContextMenu(self):
		self.syslogger('context menu not implemented ')
		self.selectedItem = self.getCurrentListPosition()
		mypath = self.getListItem(self.selectedItem).getProperty('path')
		myipath = self.getListItem(self.selectedItem).getProperty('ipath')
		mymtype = self.getListItem(self.selectedItem).getProperty('MType')
		mydialog = xbmcgui.Dialog()
		myret = mydialog.select('Choose action', ['Add to Favourites', 'XDG-Open', 'Execute', 'Copy path to clipboard', 'Copy action to clipboard', 'Import File'])
		if myret == 0:
		  self.syslogger('context add favourite '+mypath)
		elif myret == 1:
		  self.syslogger('context xdg-open '+myipath)
		  os.system("xdg-open '"+myipath+"'")
		elif myret == 2:
		  if mymtype == 'rom':
		    mycmd = "python /home/inf0rmix/emuexec-thumbnailer '"+myipath.replace("'","\\'")+"'"
		    #self.syslogger("context execute-rom  "+mycmd)
		    os.system(mycmd)
		  else:
		    self.syslogger("context execute '"+mypath+"'")
		elif myret == 3:
		  self.syslogger('context CopyToClipboard '+mypath)
		  cb_set(mypath)
		elif myret == 5:
		  self.syslogger('context ImportFile '+mypath)
		  dialog = xbmcgui.Dialog()
		  mystartpath = XBMC_ADDON.getSetting("dlgDefaultDir")
		  mypath = dialog.browse(1,'Select file to import', 'files', '', False, False,mystartpath)
		  mynewpath = os.path.dirname(mypath)
		  XBMC_ADDON.setSetting("dlgDefaultDir",mynewpath)
		  #self.syslogger('context cp '+mypath+' ' + self.basedir)
		  sh_copy(mypath,self.basedir)
		  
		elif myret == 4:
		  if mypath.startswith('RunScript('):
		    if mypath.find('?/') > -1:
		      mypath = '/' + mypath.rsplit('?/',1)[1].rstrip(')')
		      self.syslogger('context menu 3 '+mypath)
		      cb_set(mypath)
		#import dialogcontextmenu
		#constructorParam = "720p"
		#cm = dialogcontextmenu.ContextMenuDialog("script-RCB-contextmenu.xml", util.getAddonInstallPath(), "Default", constructorParam, gui=self)
		#del cm
		return True

	def xlogger(self,mylogentry='ximsg'):
		self.filelogger(mylogentry)
		#self.xbmclogger(mylogentry)

	def syslogger(self,mylogentry='ximsg'):
		mylogentry = "'" + str(mylogentry).replace("'","\\'") + "'"
		os.system('logger -t xbmc-plugin-xi -- '+mylogentry)

	def xbmclogger(self,mylogentry='ximsg'):
		xbmc.log(str(mylogentry))

	def filelogger(self,mylogentry='ximsg'):
		f = open('/tmp/xi.log','a')
		f.write(str(mylogentry)+'\n')
		f.close()

if __name__ == "__main__":
	#window = XIWindow("MyPics.xml", os.getcwd(), listing='')
	globalpath = os.getcwd()
	os.system('logger mypwdglobal: -- '+globalpath)
	#globalpath = XBMC_ADDONPATH
	#globalpath = 'plugin://plugin.program.xi/'
	#window = XIWindow("MyPrograms.xml", globalpath)
	#os.system('logger started handle x')
	window = XIWindow("eXtensibleInterface.xml", globalpath)
	window.doModal(True)
	#window.show()
	del window
	#os.system('logger stopped handle x')