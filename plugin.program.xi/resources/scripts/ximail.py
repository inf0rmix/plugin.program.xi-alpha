#!/usr/bin/python
import xbmc, xbmcgui
from sys import argv as sys_argv
from os import popen as os_popen
from os import system , getenv

def get_args(myargvstr):
  myto , mymsgfile = myargvstr.split(':',1)
  return myto , mymsgfile

def get_action(myto , mymsgfile):
  mydialog = xbmcgui.Dialog()
  myret = mydialog.select('Choose action', ['View Mail', 'Reply', 'Send File'])
  if myret == 0:
    xbmc.executebuiltin('RunScript(special://home/addons/plugin.program.xi/resources/scripts/textview.py,'+mymsgfile+')')
  elif myret == 1:
    do_reply(myto)
  elif myret == 2:
    xbmc.executebuiltin('RunScript(special://home/addons/plugin.program.xi/resources/scripts/sendfilemail.py,'+myaddr+':TODO)')

def do_reply(myrecp):
  mytitle = 'eMail - ' + myrecp
  keyboard = xbmc.Keyboard('',mytitle)
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    mystr = keyboard.getText()
    mycmd = "echo '"+mystr+"' | mutt -s '"+mystr+"' '"+myrecp+"'"
    #system('logger sendim -- '+myrecp+' str '+mystr)
    system(mycmd)

def Main():
    myto , mymsgfile = get_args(sys_argv[1])
    get_action(myto , mymsgfile)

Main()
