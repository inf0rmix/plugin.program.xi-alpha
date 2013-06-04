import xbmc, xbmcgui
from sys import argv as sys_argv
from os import path , popen

#OURSCRIPT = path.realpath(__file__)
#OURDIR = path.dirname(OURSCRIPT)
OURDIR = 'special://home/addons/plugin.program.xi/resources/scripts'

XBMC_ADDONID = 'plugin.program.xi'
XBMC_ADDONPATH = xbmc.translatePath('special://home/addons/' + XBMC_ADDONID)

##
## Base
##

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

##
## Cliviewer
##

class DialogTextViewer( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.heading = kwargs.get( "heading" )
        self.text = kwargs.get( "text" )
        xbmc.sleep( 100 )

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



##
## Dialogs
##

def dlg_cli_view(mycmd):
  myheading = 'Output of: '+mycmd
  mytext = system_popen(mycmd)
  w = DialogTextViewer( "XiDialogTextViewer.xml", XBMC_ADDONPATH, heading=myheading, text=mytext )
  w.doModal(True)
  del w

def dlg_msg_view(mycmd):
  mydialog = xbmcgui.Dialog()
  myheading = 'Output of: '+mycmd
  mytext = system_popen(mycmd)
  mylines = mytext.split('\n')
  if len(mylines) >= 3:
    myret = mydialog.ok(myheading, mylines[0], mylines[1], mylines[2])
  else:
    myret = mydialog.ok(myheading, mytext)
  return myret

def dlg_view(mycmd):
  dlg_cli_view(mycmd)

def dlg_get_command():
  keyboard = xbmc.Keyboard('','Enter command...')
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    return keyboard.getText()
  else:
    return ''

def dlg_get_action():
  mydialog = xbmcgui.Dialog()
  mylist = ['ReRun command' , 'Auto ReRun command' , 'New command', 'Exit console']
  myret = mydialog.select('Choose an action playlist', mylist)
  return myret

##
## Main
##

def MainMenu(mycmd):
  myint = dlg_get_action()
  if myint == 0:
    dlg_view(mycmd)
    return True , mycmd
  elif myint == 1:
    myiters = 5
    mycmd = dlg_get_command()
    for myiter in range(0,myiters):
      dlg_view(mycmd)
    return True , mycmd
  elif myint == 2:
    mycmd = dlg_get_command()
    dlg_view(mycmd)
    return True , mycmd
  else:
    return False , ''

def MainLoop(mycmd):
  myval , mylcmd = MainMenu(mycmd)
  while myval:
    myval , mylcmd = MainMenu(mylcmd)
  return

def Main():
  mycmd = dlg_get_command()
  if mycmd != '':
    dlg_view(mycmd)
    MainLoop(mycmd)



if ( __name__ == "__main__" ):
  Main()