import xbmc, xbmcgui
from sys import argv as sys_argv
from os import popen as os_popen
from os import system

def get_args(myargvstr):
  myto , mysubj = myargvstr.split(':',1)
  return myto , mysubj

def Main():
    myto , mysubj = get_args(sys_argv[1])
    keyboard = xbmc.Keyboard('','Send mail to: '+myto)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      mystr = keyboard.getText()
      system('logger sendmail -- '+myto+' str '+mystr)


if ( __name__ == "__main__" ):
    Main()
