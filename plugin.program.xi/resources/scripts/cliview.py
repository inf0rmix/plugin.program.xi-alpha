# Modules general
import os
from traceback import print_exc
#Argv + base64-dec
from sys import argv as sys_argv
from urllib import unquote_plus
#from urllib import urlencode
# Modules XBMC
import xbmcgui
from xbmcaddon import Addon
from xbmc import sleep

XBMC_ADDONID = 'plugin.program.xi'
XBMC_ADDONPATH = xbmc.translatePath('special://home/addons/' + XBMC_ADDONID)

class DialogTextViewer( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.heading = kwargs.get( "heading" )
        self.text = kwargs.get( "text" )
        sleep( 100 )

    def onInit( self ):
        try:
            self.getControl( 1 ).setLabel( self.heading )
            self.getControl( 5 ).setText( self.text )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        pass

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self.close()

def file_read(myfile):
  if os.path.exists(myfile):
    f = open(myfile, 'r')
    data = f.read()
    f.close()
    return data
  else:
    return ''

#def system_popen(mycmd):
  #return os.popen(mycmd, 'r').read()
from sys import stdout as sys_stdout
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

import subprocess 

def system_popen_sub(mycmd):
  p = subprocess.Popen(mycmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,close_fds=True,shell=True).stdout
  mydata = p.read()
  return mydata

def showText( heading="", text="" ):
    w = DialogTextViewer( "XiDialogTextViewer.xml", XBMC_ADDONPATH, heading=heading, text=text )
    w.doModal(True)
    del w

def get_argv():
  mycli , myargs = '' , len(sys_argv)
  for mypos in range(1,myargs):
    mycli += sys_argv[mypos] + ' '
  return mycli.rstrip(' ')

def get_head(mycmd):
  myhead = 'Cli-Viewer - '
  if len(mycmd) >= 10:
    myhead += mycmd[:10]
  else:
    myhead += mycmd
  return myhead

def Main():
  myargv = get_argv()
  myhead = get_head(myargv)
  # .decode('utf-8')
  mytxt = system_popen(myargv)
  #mytxt = '/home\n inf0rmix\n root'
  showText(myhead,mytxt)

if ( __name__ == "__main__" ):
  Main()
  #mytxt = file_read('/tmp/out.txt')

