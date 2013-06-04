#!/usr/bin/python
import xbmc, xbmcgui
from sys import argv as sys_argv
from os import path , popen , system

XBMC_XIPLUGINPATH = xbmc.translatePath('special://home/addons/plugin.program.xi/resources/xiplugins')

#Open system-command in a pipe and return data
def system_popen(cmd):
  mypipe = popen(cmd, 'r')
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

def split_xipluginurl(myurl):
  myplug = myurl[11:]
  if myplug.find('/') > -1:
    myplug , myarg = myplug.split('/',1)
  else:
    myarg = ''
  #Real Plugin path
  myplugpath = XBMC_XIPLUGINPATH + '/' + myplug + '.py'
  return myplugpath , myarg

#Split $Pluginname.(://).$Location
def split_genericurl(myurl):
  myplug , myarg = myurl.split('://',1)
  #Real Plugin path
  myplugpath = XBMC_XIPLUGINPATH + '/' + myplug + '.py'
  return myplugpath , myarg

def play_final(myxplsfile):
  myfinaluri = 'PlayMedia(plugin://plugin.program.xi/?path='+myxplsfile+')'
  xbmc.executebuiltin(myfinaluri)

def get_plugin_xpls(myurl):
  system('logger xipluginarg: -- '+myurl)
  if myurl.startswith('xiplugin://'):
    myplugscript , myarg = split_xipluginurl(myurl)
  else:
    myplugscript , myarg = split_genericurl(myurl)
  myplugcmd = "python '"+myplugscript+"' '"+myarg+"'"
  myplugxpls = system_popen(myplugcmd).strip('\n')
  return myplugxpls

def Main():
    myarg , myxpls = sys_argv[1] , ''
    if myarg.find('://') > -1:
      myxpls = get_plugin_xpls(myarg)
      if myxpls.endswith('.xpls'):
	play_final(myxpls)

if ( __name__ == "__main__" ):
    Main()

