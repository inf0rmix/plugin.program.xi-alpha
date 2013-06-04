import xbmc, xbmcgui
from sys import argv as sys_argv
from os import path , popen
import email

def mail_reader(raw_message):
  msg = email.message_from_string(raw_message)
  myout = ''
  for part in msg.walk():
      if part.get_content_type() == 'text/plain':
	  myout += str(part.get_payload()).rstrip('\n') + '\n'
  return myout

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
        self.getFile()
        # set controls
        self.setControls()
        
    def setControls( self ):
        #get header, text
        heading = path.basename(self.myfile)
        text = self.readFile(self.myfile)
        # set heading
        self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s" % ( heading, 'MailViewer', ) )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

    def getFile(self):
	if len(sys_argv) == 2:
	  self.myfile = sys_argv[1]
	else:
	  self.myfile = '/dev/null'
	  mydlg = xbmcgui.Dialog()
	  self.myfile = mydlg.browse(1, 'XBMC', 'Select Mail-File to view...', '', False, False, '/')
	  #TODO:File-Select-Dialog

    def readFile( self, filename ):
	myrawdata = open( filename ).read()
	return mail_reader(myrawdata)

def Main():
    Viewer()
    #xbmc.log( __addonname__ + ': ' + str( e ), xbmc.LOGERROR )



if ( __name__ == "__main__" ):
    Main()
