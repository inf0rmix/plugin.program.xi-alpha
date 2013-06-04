import xbmc, xbmcgui
from sys import argv as sys_argv
from os import popen as os_popen
from os import system , getenv

def get_args(myargvstr):
  myproto , myrecp = myargvstr.split(':',1)
  return myproto , myrecp

def Main():
    myproto , myrecp = get_args(sys_argv[1])
    mytitle = myproto.upper() + ' - ' + myrecp
    keyboard = xbmc.Keyboard('',mytitle)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      mystr = keyboard.getText()
      mycmd = "python ~/.purple/qim.py sendmsg "+myrecp+" '"+mystr+"'"
      #system('logger sendim -- '+myrecp+' str '+mystr)
      system(mycmd)

Main()
