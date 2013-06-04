import xbmc, xbmcgui
from os import system , popen , path , getenv
OURFIFO = getenv('HOME')+'/.xbmc/temp/.qwebview.fifo'

#get actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h

ACTION_NONE =  0
ACTION_MOVE_LEFT =  1
ACTION_MOVE_RIGHT =  2
ACTION_MOVE_UP =  3
ACTION_MOVE_DOWN =  4
ACTION_PAGE_UP =  5
ACTION_PAGE_DOWN =  6
ACTION_SELECT_ITEM = 7
ACTION_SHOW_INFO = 11
ACTION_PREVIOUS_MENU = 10
ACTION_NEXT_ITEM =  14
ACTION_PREV_ITEM =  15
ACTION_VOLUME_UP = 88
ACTION_VOLUME_DOWN = 89
ACTION_CONTEXT_MENU = 117

##FirefoxHistorySqlite for places.sqlite
#select url,title,favicon_id from moz_places where hidden=0 order by last_visit_date DESC Limit 1

#Open system-command in a pipe and return data

#def system_popen(cmd):
  #stream = popen(cmd, 'r')
  #lines = stream.read()
  #stream.close()
  #return lines

def write_to_fifo(myval):
  if not path.exists(OURFIFO):
    return False
  try:
    myfifo_write = open(OURFIFO, 'w')
  except:
    return False
  #system('echo -n '+str(myval)+' >> /tmp/tfifo')
  try:
    myfifo_write.write(str(myval))
    myfifo_write.flush()
    myfifo_write.close()
  except:
    return False
  return True

class MyClass(xbmcgui.WindowDialog):
  def __init__( self, *args, **kwargs ):
    #self.strActionInfo = xbmcgui.ControlLabel(100, 120, 200, 200, '', 'font13', '0xFFFF00FF')
    #self.addControl(self.strActionInfo)
    #self.strActionInfo.setLabel('Push BACK to quit')
    self.button0 = xbmcgui.ControlButton(350, 500, 80, 30, "HELLO")
    self.addControl(self.button0)
    self.setFocus(self.button0)
    True

  def onAction(self, action):
    myret = False
    if action == ACTION_MOVE_UP:	myret = write_to_fifo(ACTION_MOVE_UP)
    elif action == ACTION_MOVE_DOWN:	myret = write_to_fifo(ACTION_MOVE_DOWN)
    elif action == ACTION_SELECT_ITEM:	myret = write_to_fifo(ACTION_SELECT_ITEM)
    elif action == ACTION_MOVE_LEFT:	myret = write_to_fifo(ACTION_MOVE_LEFT)
    elif action == ACTION_MOVE_RIGHT:	myret = write_to_fifo(ACTION_MOVE_RIGHT)
    elif action == ACTION_PAGE_UP:	myret = write_to_fifo(ACTION_PAGE_UP)
    elif action == ACTION_PAGE_DOWN:	myret = write_to_fifo(ACTION_PAGE_DOWN)
    elif action == ACTION_CONTEXT_MENU:	myret = write_to_fifo(ACTION_CONTEXT_MENU)
    elif action == ACTION_SHOW_INFO:	myret = write_to_fifo(ACTION_SHOW_INFO)
    elif action == ACTION_VOLUME_UP:	myret = write_to_fifo(ACTION_VOLUME_UP)
    elif action == ACTION_VOLUME_DOWN:	myret = write_to_fifo(ACTION_VOLUME_DOWN)
    elif action == ACTION_PREVIOUS_MENU:
      write_to_fifo(0)
      self.close()
      system('logger -t xbmc aclose')
    else:
      #print 44444,action
      system('logger -t xbmc aelse')
      #myret = write_to_fifo(ACTION_PREVIOUS_MENU)
      #self.close()
    if myret == False:
      system('logger -t xbmc closing')
      self.close()

  def onControl(self, control):
    write_to_fifo(ACTION_SELECT_ITEM)
    #if control == self.button0:
      ###self.message('you pushed the button')
      ##system('logger -t xbmc sel1')
      #write_to_fifo(ACTION_SELECT_ITEM)
      #system('logger -t xbmc sel2')
    #else:
    #system('logger -t xbmc control')
 
  def message(self, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(" My message title", message)
 
mydisplay = MyClass()
mydisplay .doModal()
del mydisplay

