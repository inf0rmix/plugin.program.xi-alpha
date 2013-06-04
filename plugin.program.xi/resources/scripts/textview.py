# Modules general
import os
from traceback import print_exc
#Argv + base64-dec
from sys import argv as sys_argv
from urllib import unquote_plus
#from urllib import urlencode
# Modules XBMC
import xbmcgui
from xbmc import translatePath , sleep

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


def showText( heading="", text="" ):
    mytsplit = text.split('\n')
    w = DialogTextViewer( "XiDialogTextViewer.xml", XBMC_ADDONPATH, heading=heading, text=text )
    w.doModal()
    del w

def get_argv():
  mycli , myargs = '' , len(sys_argv)
  for mypos in range(1,myargs):
    mycli += sys_argv[mypos] + ' '
  return mycli.rstrip(' ')

def get_text(mymode,myfile):
  if mymode == 'cat':
    mytext = system_popen("cat '"+myfile+"' | tail -n 4000")
  elif mymode == 'tac':
    mytext = system_popen("tac '"+myfile+"' | head -n 4000")
  elif mymode == 'head':
    mytext = system_popen("head -100 '"+myfile+"'")
  elif mymode == 'tail':
    mytext = system_popen("tail -100 '"+myfile+"'")
  return mytext
	

def getInput():
  if len(sys_argv) == 2:
    myargv = sys_argv[1]
    if myargv.find(':')> -1:
      mymode , myfile = myargv.split(':',1)
      return myfile , get_text(mymode , myfile)
  return '' , ''

#mytxt = file_read('/tmp/out.txt')
# .decode('utf-8')
if ( __name__ == "__main__" ):
  myfile , mytxt = getInput()
  showText(myfile,mytxt)

