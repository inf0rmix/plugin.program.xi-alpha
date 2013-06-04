import xbmc , xbmcgui , os , urllib2
from datetime import datetime

BPATH=xbmc.translatePath('special://profile')
OUTDIR={}
OUTDIR['audio'] = BPATH + 'recordings/audio'
OUTDIR['video'] = BPATH + 'recordings/video'
ADDTOPLS=True

#Date as string
def get_datetime():
  now = datetime.now()
  return now.strftime("%Y-%m-%d_%H-%M")

#Write text-file
def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

#Append to text-file
def file_append(myfile,mytxt):
  f = open(myfile, 'a')
  f.write(mytxt)
  f.close()

#Perform HEAD-Request and pass Content-Type
def get_http_mimetype(myurl):
  mysheaders = { 'User-Agent' : ' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0' }
  myhreq = urllib2.Request(myurl, None, mysheaders)
  myreq = urllib2.urlopen(myhreq)
  myhead = myreq.info()
  #Get Content-Type
  try:
    mytype = myhead['Content-Type']
  except:
    mytype = ''
  if mytype.find(';') > -1:
    mytype = mytype.split(';',1)[0]
  #Get Length if not a stream
  if myhead.has_key('Content-Length'):
    myisstream = False
  else:
    myisstream = True
  #Close Request
  try:
    myreq.close()
  except:
    True
  #Set output suffix
  if mytype == 'audio/mpeg':
    mysuf = 'mp3'
  elif mytype == 'video/x-flv':
    mysuf = 'mp4'
  elif mytype == 'application/x-mpegURL':
    myisstream , mysuf = True , 'mp4'
  else:
    mysuf = mytype.split('/')[1]
  return mytype,mysuf,myisstream

def get_playerinfo():
  myquery = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}')
  mysplit = str(myquery).split('"')
  if len(mysplit) > 5:
    if mysplit[-4] == 'type':
      mytype = mysplit[-2]
      myid = mysplit[-5].strip(',:')
      return myid , mytype
  return '0' , ''

def get_outdir(mytype):
  if OUTDIR.has_key(mytype):
    mydir = OUTDIR[mytype]
    if not os.path.exists(mydir):
      os.makedirs(mydir)
    return mydir
  else:
    return BPATH+'recordings'

#Get property from json query string
def parse_json_property(myjson,myprop):
  myret , mysstr = '' , '"'+myprop+'":"'
  if myjson.find(mysstr) >-1:
    myjson = myjson.split(mysstr,1)[1]
    myret = myjson.split('"',1)[0]
  return myret

def get_active():
  myid , mytype = get_playerinfo()
  if mytype == 'audio':
    myquery = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "duration", "thumbnail", "file", "fanart", "streamdetails"], "playerid": '+myid+'}, "id": "AudioGetItem"}')
  elif mytype == 'video':
    myquery = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "duration", "thumbnail", "file", "fanart", "streamdetails"], "playerid": '+myid+'}, "id": "VideoGetItem"}')
  else:
    return '','',''
  #Split at file-prop
  myfile = parse_json_property(myquery,'file')
  mytitle = parse_json_property(myquery,'label')
  if mytitle == '':
    mytitle = parse_json_property(myquery,'title')
  mytitle = mytitle.replace("'",'').replace(":",'').replace("`",'').replace("'",'').replace("$",'').replace("!",'')
  mytitle = mytitle.replace(" - ",'-').replace(" ",'_')
  return mytype,myfile,mytitle

def get_kbstr(mytemp='',mytitle=''):
  if mytemp == '':
    mytemp = get_datetime()
  #get from keyboard
  keyboard = xbmc.Keyboard(mytemp,mytitle)
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    mytxt = keyboard.getText()
  else:
    mytxt = ''
  return mytxt

def get_duration():
  dialog = xbmcgui.Dialog()
  mynum = dialog.numeric(0, 'Minutes to record...',"30")
  mysecs = int(mynum)*60
  return str(mysecs)

def add_to_playlist(mytype,mypath,mytitle,mydur='0'):
  if mytype == 'audio':
    myplsfile = BPATH + 'playlists/music/Recordings.m3u'
  else:
    myplsfile = BPATH + 'playlists/video/Recordings.m3u'
  if not os.path.exists(myplsfile):
    file_write(myplsfile,'#EXTM3U\n')
  file_append(myplsfile,'#EXTINF:'+mydur+','+mytitle+'\n'+mypath+'\n')

def record_pressed():
  mytype,myfile,mytitle = get_active()
  mydopt , mydur = '' , '0'
  if mytype == 'audio':
    mycopt = '-vn -acodec copy'
  elif mytype == 'video':
    mycopt = '-vcodec copy -acodec copy'
  if myfile.startswith('http://') or myfile.startswith('https://'):
    mymime , mysuf , myisstream = get_http_mimetype(myfile)
    mydur = '0'
    if myisstream:
      mydur = get_duration()
      mydopt = '-t '+mydur
      if mytype == 'audio':
	mycopt = '-vn -acodec libmp3lame'
	mysuf = 'mp3'
    myftitle = get_kbstr(mytitle,'Enter filename...')
    myout = get_outdir(mytype)+'/'+myftitle+'.'+mysuf
    mycmd = "avconv -y -i '"+myfile+"' "+mydopt+" "+mycopt+" '"+myout+"'"
    if os.path.exists(myout):
      xbmc.executebuiltin('notification(Output-File already exists:,'+myout+')')
    else:
      xbmc.executebuiltin('notification(Saving to:,'+myout+')')
      os.system(mycmd+" >/dev/null 2>&1 &")
      add_to_playlist(mytype,myout,myftitle,mydur)
    os.system("logger figgn -- '"+mycmd+"'")
  elif myfile.startswith('rtmp://') or myfile.startswith('rtsp://'):
    myftitle = get_kbstr(mytitle,'Enter filename...')
    mysuf='mp4'
    mydur = get_duration()
    mydopt = '-t '+mydur
    myout = get_outdir(mytype)+'/'+myftitle+'.'+mysuf
    mycmd = "avconv -y -i '"+myfile+"' "+mydopt+" "+mycopt+" -f mp4 '"+myout+"'"
    if os.path.exists(myout):
      xbmc.executebuiltin('notification(Output-File already exists:,'+myout+')')
    else:
      xbmc.executebuiltin('notification(Streaming to:,'+myout+')')
      os.system(mycmd+" >/dev/null 2>&1 &")
      add_to_playlist(mytype,myout,myftitle,mydur)
    os.system("logger figgn -- '"+mycmd+"'")

#mystr = get_active().replace("'",'')
#os.system("logger figgn -- '"+mystr+"'")
record_pressed()
