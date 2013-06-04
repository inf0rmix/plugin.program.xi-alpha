import xbmc, xbmcgui
from sys import argv as sys_argv
from os import path , popen

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

class Viewer:
    # constants
    WINDOW = 10147
    CONTROL_LABEL = 1
    CONTROL_TEXTBOX = 5

    def __init__( self, *args, **kwargs ):
        # activate the text viewer window
        xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
        # get window
        self.window = xbmcgui.Window( self.WINDOW )
        # give window time to initialize
        xbmc.sleep( 100 )
        #Get file path from argv or dialog
        self.getArgs()
        # set controls
        self.setControls()
        
    def setControls( self ):
        #get header, text
        heading = path.basename(self.myfile)
        if self.mymode == 'cat':
	  text = self.readFile(self.myfile)
	elif self.mymode == 'tac':
	  text = system_popen("tac '"+self.myfile+"'")
	elif self.mymode == 'head':
	  text = system_popen("head -100 '"+self.myfile+"'")
	elif self.mymode == 'tail':
	  text = system_popen("tail -100 '"+self.myfile+"'")
	
        # set heading
        self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s" % ( heading, 'TextViewer', ) )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

    def getArgs(self):
	if len(sys_argv) == 2:
	  self.myargv = sys_argv[1]
	  if self.myargv.find(':')> -1:
	    self.mymode , self.myfile = self.myargv.split(':',1)
	  else:
	    self.myfile = sys_argv[1]
	    self.mymode = 'cat'
	else:
	  self.myfile = '/etc/passwd'
	  self.mymode = 'cat'
	  #mydlg = xbmcgui.Dialog()
	  #self.myfile = mydlg.browse(1, 'XBMC', 'Select File to view...', '', False, False, '/')
	  ##TODO:File-Select-Dialog

    def readFile( self, filename ):
	if filename.startswith('http://') or filename.startswith('https://'):
	  mywgetcmd = "wget -O - -q '"+filename+"'" #todo: substitute wget
	  return popen(mywgetcmd, 'r').read()
	else:
	  return open( filename ).read()

def Main():
    Viewer()
    #xbmc.log( __addonname__ + ': ' + str( e ), xbmc.LOGERROR )



if ( __name__ == "__main__" ):
    Main()
