import xbmc, xbmcgui
import base64
from sys import argv as sys_argv
from os import path , popen

#Does not show all the text - TODO seek for an alternative
def Viewer_Dialog():
  if len(sys_argv) == 2:
    mytext = sys_argv[1]
  else:
    mytext = 'Empty'
  #get header, text
  myheading = 'MyHead'
  mytext = base64.b64decode(mytext)
  mydlg = xbmcgui.Dialog()
  mydlg.ok(myheading,mytext)

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
        #Get text from argv -> decode base64 -> set controls
        self.setControls()
        
    def setControls( self ):
	if len(sys_argv) == 2:
	  myintext = sys_argv[1]
	else:
	  myintext = 'Empty'
        #get header, text
        myparts = myintext.split(':')
        mytext = base64.b64decode(myparts[1])
        myhead = base64.b64decode(myparts[0])
        # set heading
        self.window.getControl( self.CONTROL_LABEL ).setLabel(myhead )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( mytext )

if ( __name__ == "__main__" ):
    Viewer()
