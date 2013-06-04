# -*- coding: utf-8 -*-
#icon:view-history
from sys import exit as sys_exit
from sys import argv as sys_argv
from os import popen , getenv
try:
  import xbmc , xbmcgui
  OURMODE='1'
except:
  OURMODE='0'
import os


OURXPLSDIR=getenv('HOME')+'/.local/xpls'

if OURMODE=='1':
  XBMCXIPATH=xbmc.translatePath('special://home/addons/plugin.program.xi/resources/scripts')
else:
  XBMCXIPATH=getenv('HOME')+'/.xbmc/addons/plugin.program.xi/resources/scripts'

#Open system-command in a pipe and return data
def system_popen(mycmd):
  try:
    return popen(mycmd, 'r').read()
  except:
    return ''

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

def dlg_get_string():
  keyboard = xbmc.Keyboard('','Enter command...')
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    myret = keyboard.getText()
    return True , myret
  else:
    return False , ''

def format_list(mydata,myarg=''):
  for myline in mydata.split('\n'):
    mydata += '1\techo\t'+myline+'\tls\t\n'
  return mydata


def get_xpls():
  myicon = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/website.png'
  mycmd = system_popen('xbmcdialog --inputbox command:')
  mylist = system_popen(mycmd)
  mydata = format_list(mylist)
  return mydata

#Plugin-Mode
print get_xpls().rstrip('\n')
