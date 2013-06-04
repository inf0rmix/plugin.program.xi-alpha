#icon:view-history
from sys import exit as sys_exit
from sys import argv as sys_argv
try:
  import xbmc , xbmcgui
  OURMODE='1'
except:
  OURMODE='0'
import os


OURXPLSDIR=os.getenv('HOME')+'/.local/xpls'

if OURMODE=='1':
  XBMCXIPATH=xbmc.translatePath('special://home/addons/plugin.program.xi/resources/scripts')
else:
  XBMCXIPATH=os.getenv('HOME')+'/.xbmc/addons/plugin.program.xi/resources/scripts'

#Open system-command in a pipe and return data
def system_popen(mycmd):
  try:
    return os.popen(mycmd, 'r').read()
  except:
    return ''

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

OURSQLFILE=system_popen('ls -1t $HOME/.mozilla/firefox/*.default/places.sqlite | head -1').rstrip('\n')

def get_history():
  mytret ,myuret ,mydret ,myiret = [],[],[],[]
  if OURSQLFILE != '':
    mysqlitecmd = "sqlite3 '"+OURSQLFILE+"'"
    mysqlitecmd += " 'select url,title,favicon_id,last_visit_date from moz_places where hidden=0 order by last_visit_date DESC Limit 10'"
    print mysqlitecmd
    mysqliteres = system_popen(mysqlitecmd).rstrip('\n')
    for myline in mysqliteres.split('\n'):
      mysplit = myline.split('|')
      if len(mysplit) == 4:
	myuret.append(mysplit[0])
	mytret.append(mysplit[1])
	myiret.append(mysplit[2])
	mydret.append(mysplit[3])
  return mytret,myuret,myiret,mydret

def select_history():

  mythist , myuhist , myihist , mydhist = get_history()

  dialog = xbmcgui.Dialog()
  myint = dialog.select('Select from Firefox-History...', mythist)
  try:
    myurl = myuhist[myint]
  except:
    myurl = ''
  os.system("logger int: -- '"+str(myurl)+"'")
  return myurl

def view_history():
  myurl = select_history()
  if myurl.startswith('http'):
    os.system('python '+XBMCXIPATH+"/qwebview view '"+myurl+"' &")
  else:
    xbmc.executebuiltin('Notification(Unknown URL for qwebview:,'+myurl+')')

def get_xpls():
  mythist , myuhist , myihist , mydhist = get_history()
  myicon = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/website.png'
  mydata = ''
  for i in range(0,len(mythist)):
    myuri = 'RunScript(special://home/addons/plugin.program.xi/run.py,web?'+myuhist[i]+')'
    mydata += mydhist[i]+'\tweb\t'+mythist[i] + '\t' + myuri + '\t' + myicon + '\n'
  return mydata

#Plugin-Mode
if OURMODE=='0':
  #TODO: Check for given output-file via ARGV
  if len(sys_argv) >= 2:
    ouroutfile=sys_argv[1]
    ouroutdata = get_xpls()
    file_write(ouroutfile,ouroutdata)
    print myoutdata
  else:
    print get_xpls().rstrip('\n')

else:

  view_history()
