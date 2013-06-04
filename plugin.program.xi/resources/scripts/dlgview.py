#!/usr/bin/python
import xbmc , xbmcgui
from os import path , popen , getenv , system
from hashlib import md5
from time import mktime
from sys import argv
import base64
import vobject
XBMC_VIEWERTEXT = ''
DLG_PIPECMD = ''
PIPETEMPFILE = '/tmp/pipetest.txt'
XBMC_ADDONID = 'plugin.program.xi'
XBMC_USERDATAPATH = xbmc.translatePath('special://profile')
XBMC_ADDONPATH = xbmc.translatePath('special://home/addons/' + XBMC_ADDONID)

OUREVICON = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/text-vcalendar.png'
OURSCRIPTURI='RunScript(special://home/addons/plugin.program.xi/resources/scripts/textbox.py,%%XIARG%%)'
OURXPLSDIR = getenv('HOME')+'/.local/xpls'
OURTHUMBDIR = getenv('HOME')+'/.thumbnails'
OURICONBG = getenv('HOME')+'/.xbmc/addons/plugin.program.xi/resources/skins/Default/media/icon-backdrop.png'

def file_read(myfile):
  if path.exists(myfile):
    f = open(myfile, 'r')
    data = f.read()
    f.close()
    return data
  else:
    return ''

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

def system_popen(mycmd):
  return popen(mycmd, 'r').read()

def find_xdg_icon(myicon):
  myiconfile = ''
  mylist = system_popen('ls -1 /usr/share/icons/default.*/*/*/'+myicon+'.png')
  if mylist.find('\n') > -1:
    myiconfile = mylist.split('\n')[0]
  else:
    mylist = system_popen('ls -1 /usr/share/icons/*/*/*/'+myicon+'.png')
    if mylist.find('\n') > -1:
      myiconfile = mylist.split('\n')[0]
  return myiconfile

def get_entry_icon(myicon):
  if myicon.startswith('xdgicon://'):
    myiconname = myicon[10:]
  elif myicon != '' and myicon.find('/') == -1:
    myiconname = myicon
  #TODO: does not work for http:// !
  if myiconname != '':
    myiconfile = OURTHUMBDIR+'/'+myiconname+'.png'
    if path.exists(myiconfile):
      return myiconfile
    else:
      myrealiconfile = find_xdg_icon(myiconname)
      mygcmd = 'convert '+myrealiconfile+' -resize 128x128 - | composite -gravity center - '+OURICONBG+' '+myiconfile
      system(mygcmd)
      return myiconfile
  else:
    return myicon
      

def get_dialog_struct(myxidlgfile):
  myret , mycnt = '' , 0
  mydata = file_read(myxidlgfile)
  for myline in mydata.split('\n'):
    mysplit = myline.split('\t')
    if len(mysplit) >= 3:
      if len(mysplit) == 3:
	myicon = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/dlg-'+mysplit[0]+'.png'
      else:
	myicon = get_entry_icon(mysplit[3])
      myuri = 'dlg://'+mysplit[0]+':'+mysplit[2]
      mycnt += 1
      myret += str(mycnt)+'\tdlg'+'\t'+mysplit[1]+'\t'+myuri+'\t'+myicon+'\n'
      #myret['title'].append(mysplit[1])
      #myret['arg'].append(mysplit[2])
  return myret

###
### Text-Viewer-Class
###

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
        #self.getFile()
        # set controls
        self.setControls()
        
    def setControls( self ):
        #get header, text
        heading = 'CLI-Output' #path.basename(self.myfile)
        #mytext = XBMC_VIEWERTEXT
        self.dlgrun_main(argv[1])
        mytext = system_popen(DLG_PIPECMD)
        #mytext = '123\n1233\n'# self.readFile(self.myfile)
        # set heading
        self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s" % ( heading, 'TextViewer', ) )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( mytext )

    def getFile(self):
	self.myfile = PIPETEMPFILE

    def readFile( self, filename ):
	return open( filename ).read()

    ##
    ## DLG-Main Functions
    ##

    def doDialogAction(self,mycmode,mycarg):
      #global PIPETEMPFILE
      #Perform action
      if mycmode == 'run':
	#xbmc.executebuiltin('Notification(Executing,'+mycarg+')')
	os.system(mycarg+' &')
      elif mycmode == 'int':
	#xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
	xbmc.executebuiltin(mycarg)
      elif mycmode == 'cli':
	#myclistr = mycarg.replace(' ','%20')
	#xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/cliview.py,'+myclistr+')')
	#xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/cliview.py,'+mycarg+')')
	#os.system(mycarg + ' > ' + PIPETEMPFILE)
	global XBMC_VIEWERTEXT
	global DLG_PIPECMD
	DLG_PIPECMD = mycarg
	#XBMC_VIEWERTEXT = system_popen(mycarg)
	#Viewer()
      elif mycmode == 'cmd':
	#xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
	mydialog = xbmcgui.Dialog()
	myret = system_popen(mycarg)
	mydialog.ok('Output:',myret)
      elif mycmode == 'txt':
	#xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
	xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,'+mycarg+')')
      elif mycmode == 'psel':
	#xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
	xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,'+mycarg+')')
      elif mycmode == 'tail':
	#xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
	xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/tailview.py,'+mycarg+')')

    def dlg_list_to_menu(self,mylist):
      myret = []
      mylist = mylist.replace('\n',' ').replace('\t',' ')
      for myent in mylist.split(' '):
	myret.append(myent)
      return myret

    def dlg_cmd_to_menu(self,mycmd):
      #os.system(mycmd+' > /tmp/mylist.txt')
      #mycmdout = file_read('/tmp/mylist.txt')
      mycmdout = 'inf0rmix\nroot\n' #system_popen(mycmd)
      myaret , mybret = [] , []
      for myline in mycmdout.split('\n'):
	mybret.append(myline)
	mysplit = myline.split()
	if len(mysplit) >= 2:
	  myaret.append(mysplit[0])
	else:
	  myaret.append(myline)
      return myaret , mybret

    def dlg_rewriteAction(self,mymode,myopt='',mycomment=''):
      myret , myvalid = '' , False
      if mymode == 'XISTR':
	if mycomment == '': mycomment = 'Enter String:'
	keyboard = xbmc.Keyboard('',mycomment)
	keyboard.doModal()
	if (keyboard.isConfirmed()):
	  myret = keyboard.getText()
	  myvalid = True
      elif mymode == 'XINUM':
	if mycomment == '': mycomment = 'Enter Value:'
	dialog = xbmcgui.Dialog()
	mynum = str(dialog.numeric(0, mycomment))
	if mynum.isdigit():
	  myvalid = True
	  myret = mynum
      elif mymode == 'XIFILE':
	dialog = xbmcgui.Dialog()
	mypath = dialog.browse(1,mycomment, 'files', '', False, False,'/')
	if mypath:
	  return mypath , False
	else:
	  myret = mypath
	  myvalid = True
      elif mymode == 'XIDIR':
	dialog = xbmcgui.Dialog()
	mypath = dialog.browse(0,mycomment, 'files', '', False, False,'/')
	if mypath:
	  return mypath , False
	else:
	  myret = mypath
	  myvalid = True
      elif mymode == 'XILIST':
	dialog = xbmcgui.Dialog()
	mymenu = self.dlg_list_to_menu(mycomment)
	myint = dialog.select('Select Action...',mymenu )
	myret = mymenu[myint]
	myvalid = True
      elif mymode == 'XICB': # TODO: is stub!!!!
	dialog = xbmcgui.Dialog()
	mymenu = self.dlg_list_to_menu(cb_get())
	myint = dialog.select('Select Action...',mymenu )
	myret = mymenu[myint]
	myvalid = True
      elif mymode == 'XIPIPE': #TODO: Causes 100% load
	dialog = xbmcgui.Dialog()
	dmenu_a , dmenu_b = self.dlg_cmd_to_menu(mycomment)
	myint = dialog.select('Select Action...',dmenu_b )
	myret = dmenu_a[myint]
	myvalid = True
      elif mymode == 'XICSV': # TODO: is stub!!!!
	dialog = xbmcgui.Dialog()
	mymenu = self.dlg_list_to_menu(mycomment)
	myint = dialog.select('Select Action...',mymenu )
	myret = mymenu[myint]
	myvalid = True
      return myret , myvalid

    #Rewrite URL/Path using xbmc Dialog and perform Action afterwards
    def dlg_rewritePathString(self,myurl):
      mynurl , myvalid = myurl , True
      while myvalid:
	mynurl , myvalid = self.dlg_probePathString(mynurl)
	os.system('logger True: ' +mynurl)
      return mynurl

    def dlg_probePathString(self,myurl):
      if myurl.find('%%') > -1:
	myurlpre , myurlsuf = myurl.split('%%',1)
	if myurlsuf.find('%%') > -1:
	  myrewritedata , myrest = myurlsuf.split('%%',1)
	  myrewritemode , myrewriteopt , mycomment = myrewritedata.split(':',2)
	  mydlgret , mydlgstat = self.dlg_rewriteAction(myrewritemode , myrewriteopt , mycomment)
	  mynewurl = myurlpre+mydlgret+myrest
	  #os.system('logger newurl -- ' +mynewurl)
	  return mynewurl , True
      return myurl , False

    def dlgrun_main(self,mydlguri):
      mydlgcmd=mydlguri[6:]
      mydlguri=self.dlg_rewritePathString(mydlgcmd)
      mydlgcmd , mydlgarg = mydlguri.split(':',1)
      self.doDialogAction(mydlgcmd,mydlgarg)

##
## Main Functions
##

#Parse xdg or ical file
def parse_file(myinput):
  if path.exists(myinput):
    myidata = file_read(myinput)
    mylogo = OUREVICON
    if myidata.startswith('[Desktop Entry]\n'):
      myxdata = parse_xdg_file(myinput)
      myicaldata = get_http_data(myxdata['URL'])
      #Check for logo
      if myxdata.has_key('LogoURL'):
	mylogo = myxdata['LogoURL']
      return dump_ical_xpls(myicaldata,mylogo)
    else:
      return dump_ical_xpls(myidata,mylogo)

def parse_input(myinput):
  if myinput.startswith('http://') or myinput.startswith('https://'):
    myicaldata = get_http_data(myinput)
    return dump_ical_xpls(myicaldata)
  elif myinput.startswith('/'): # TODO: file:// ??!!!
    return parse_file(myinput)

def get_xpls(myinuri):
  myxplsdata = parse_input(myinuri)
  return myxplsdata

#print parse_input('/home/inf0rmix/basic.ics')
#print 444
#if len(argv) >= 2:
  #myxplsdata = get_dialog_struct(argv[1])
#if len(argv) == 3:
  #if argv[2] == '-play':
    #myxplsfile = OURXPLSDIR + '/' + path.basename(argv[1]).replace('.','-') + '.xpls'
    #file_write(myxplsfile,myxplsdata)
    #system("xbmc-send -a 'PlayMedia(plugin://plugin.program.xi/?"+myxplsfile+")'")
  #else:
    #myxplsfile = argv[2]
    #file_write(myxplsfile,myxplsdata)
#else:
    #myxplsfile = OURXPLSDIR + '/' + path.basename(argv[1]).replace('.','-') + '.xpls'
    #file_write(myxplsfile,myxplsdata)
    #system("xbmc-send -a 'PlayMedia(plugin://plugin.program.xi/?"+myxplsfile+")'")
#print 'https://www.google.com/calendar/ical/f6q2gi6tc6jpat7o8l7upjo4ag%40group.calendar.google.com/public/basic.ics'
#print icaldate_to_date('20130424T173000Z')
#arsedCal = vobject.readComponents(mydata)
#for obj in vobject.readComponents(mydata):
  #print obj.adr

#print parsedCal.vevent.dtstart.value

#print datetime.datetime(2006, 2, 16, 0, 0, tzinfo=tzutc())
if ( __name__ == "__main__" ):
    Viewer()
    #dlgrun_main(argv[1])

