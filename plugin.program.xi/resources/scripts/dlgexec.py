#!/usr/bin/python
import xbmc, xbmcgui
from sys import argv as sys_argv
from os import popen as os_popen
from os import system , getenv
XBMC_ADDONID = 'plugin.program.xi'
XBMC_ADDONPATH = xbmc.translatePath('special://home/addons/' + XBMC_ADDONID)
##
## list
##


#Open system-command in a pipe and return data
def system_popen(cmd):
  mypipe = os_popen(cmd, 'r')
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

###
def dlg_list_to_menu(mylist):
  myret = []
  mylist = mylist.replace('\n',' ').replace('\t',' ')
  for myent in mylist.split(' '):
    myret.append(myent)
  return myret

import subprocess 

def system_subpipe(mycmd):
  p = subprocess.Popen(mycmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True).stdout
  mydata = p.read()
  print mydata
  return mydata

def dlg_cmd_to_menu(mycmd):
  
  mycmdout = system_subpipe(mycmd)
  #os.system(mycmd+' > /tmp/mylist.txt')
  #mycmdout = file_read('/tmp/mylist.txt')
  myaret , mybret = [] , []
  for myline in mycmdout.split('\n'):
    mybret.append(myline)
    mysplit = myline.split()
    if len(mysplit) >= 2:
      myaret.append(mysplit[0])
    else:
      myaret.append(myline)
  return myaret , mybret

def dlg_rewriteAction(mymode,myopt='',mycomment=''):
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
    mymenu = dlg_list_to_menu(mycomment)
    myint = dialog.select('Select Action...',mymenu )
    myret = mymenu[myint]
    myvalid = True
  elif mymode == 'XICB': # TODO: is stub!!!!
    dialog = xbmcgui.Dialog()
    mymenu = dlg_list_to_menu(cb_get())
    myint = dialog.select('Select Action...',mymenu )
    myret = mymenu[myint]
    myvalid = True
  elif mymode == 'XIPIPE': #TODO: Causes 100% load
    dialog = xbmcgui.Dialog()
    dmenu_a , dmenu_b = dlg_cmd_to_menu(mycomment)
    myint = dialog.select('Select Action...',dmenu_b )
    myret = dmenu_a[myint]
    myvalid = True
  elif mymode == 'XICSV': # TODO: is stub!!!!
    dialog = xbmcgui.Dialog()
    mymenu = dlg_list_to_menu(mycomment)
    myint = dialog.select('Select Action...',mymenu )
    myret = mymenu[myint]
    myvalid = True
  return myret , myvalid

#Rewrite URL/Path using xbmc Dialog and perform Action afterwards
def dlg_rewritePathString(myurl):
  mynurl , myvalid = myurl , True
  mycnt = 0
  while myvalid and mycnt < 100:
    mynurl , myvalid = dlg_probePathString(mynurl)
    mycnt += 1
    #os.system('logger True: ' +mynurl)
  return mynurl

def dlg_probePathString(myurl):
  if myurl.find('%%') > -1:
    myurlpre , myurlsuf = myurl.split('%%',1)
    if myurlsuf.find('%%') > -1:
      myrewritedata , myrest = myurlsuf.split('%%',1)
      myrewritemode , myrewriteopt , mycomment = myrewritedata.split(':',2)
      mydlgret , mydlgstat = dlg_rewriteAction(myrewritemode , myrewriteopt , mycomment)
      mynewurl = myurlpre+mydlgret+myrest
      #os.system('logger newurl -- ' +mynewurl)
      return mynewurl , True
  return myurl , False

##
## Action
##

def doDialogAction(mycmode,mycarg):
  #Perform action
  if mycmode == 'run':
    #xbmc.executebuiltin('Notification(Executing,'+mycarg+')')
    os.system(mycarg+' &')
  elif mycmode == 'int':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin(mycarg)
  elif mycmode == 'cli':
    xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/cliview.py,'+mycarg+')')
    #myclistr = mycarg.replace(' ','%20')
    #self.syslogger('cliviewer')
    #system("logger sys -- xbmc-send -a '"+'RunScript('+XBMC_ADDONPATH+'/resources/scripts/cliview.py,'+mycarg+")'")
  elif mycmode == 'cmd':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    mydialog = xbmcgui.Dialog()
    myret = system_popen(mycarg)
    mydialog.ok('Output:',myret)
  elif mycmode == 'cat':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,cat:'+mycarg+')')
  elif mycmode == 'tac':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,tac:'+mycarg+')')
  elif mycmode == 'tail':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,tail:'+mycarg+')')
  elif mycmode == 'head':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin('RunScript('+XBMC_ADDONPATH+'/resources/scripts/textview.py,head:'+mycarg+')')

def Main():
    myarg = sys_argv[1]
    if myarg.startswith('dlg://'):
      myarg = myarg[6:]
    mydlguri=dlg_rewritePathString(myarg)
    mydlgcmd , mydlgarg = mydlguri.split(':',1)
    #system('logger '+ mydlgcmd + mydlgarg)
    doDialogAction(mydlgcmd , mydlgarg)

Main()
