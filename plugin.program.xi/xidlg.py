# -*- coding: utf-8 -*-
import os
import xbmc , xbmcgui
from sys import argv as sys_argv

XBMCXIPATH=xbmc.translatePath('special://home/addons/plugin.program.xi/resources/scripts')

#Read file
def file_read(myfile):
  if os.path.exists(myfile):
    f = open(myfile, 'r')
    data = f.read()
    f.close()
    return data

#Open system-command in a pipe and return data
def system_popen(mycmd):
  xbmc.log('arggh1')
  try:
    myret = os.popen(mycmd, 'r').read()
  except:
    myret = ''
  xbmc.log('arggh2')
  return myret

def ok_cli_dialog(mytitle,mycmd):
  mydialog = xbmcgui.Dialog()
  myret = system_popen(mycmd)
  mydialog.ok(mytitle,myret)

##
## Main
##

#Rewrite URL/Path using xbmc Dialog and perform Action afterwards
def rewritePathString(myurl,mycomment=''):
  myvalid = False
  if myurl.find('%%XISTR%%') > -1:
    if mycomment == '': mycomment = 'Enter String:'
    keyboard = xbmc.Keyboard('',mycomment)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      mystr = keyboard.getText()
      myurl = myurl.replace('%%XISTR%%',mystr)
      myvalid = True
  elif myurl.find('%%XINUM%%') > -1:
    if mycomment == '': mycomment = 'Enter Value:'
    dialog = xbmcgui.Dialog()
    mynum = str(dialog.numeric(0, mycomment))
    if mynum.isdigit():
      myvalid = True
      myurl = myurl.replace('%%XINUM%%',mynum)
  elif myurl.find('%%XIFILE%%') > -1:
    if mycomment == '': mycomment = 'Enter Value:'
    dialog = xbmcgui.Dialog()
    mypath = dialog.browse(1,mycomment, 'files', '', False, False,'/')
    if not mypath:
      return myurl , False
    else:
      myurl = myurl.replace('%%XIFILE%%',mypath)
      myvalid = True
  elif myurl.find('%%XIDIR%%') > -1:
    if mycomment == '': mycomment = 'Enter Value:'
    dialog = xbmcgui.Dialog()
    mypath = dialog.browse(0,mycomment, 'files', '', False, False,'/')
    if not mypath:
      return myurl , False
    else:
      myurl = myurl.replace('%%XIDIR%%',mypath)
      myvalid = True
  else:
    myvalid = True
  return myurl , myvalid

def get_dialog_struct(myxidlgfile):
  myopts = {'title':'','mode':'','icon':''}
  myret = {'mode':[],'title':[],'arg':[],'opts':myopts}
  mydata = file_read(myxidlgfile)
  for myline in mydata.split('\n'):
    if myline.startswith('$'):
      if myline.find('=') > -1:
	myvar , myval = myline[1:].split('=',1)
	myopts[myvar] = myval
    else:
      mysplit = myline.split('\t')
      if len(mysplit) == 3:
	myret['mode'].append(mysplit[0])
	myret['title'].append(mysplit[1])
	myret['arg'].append(mysplit[2])
  myret['opts'] = myopts
  return myret

def maindlg(myfile):
  mystruct = get_dialog_struct(myfile)
  dialog = xbmcgui.Dialog()
  myint = dialog.select('Select Action...', mystruct['title'])
  #Exit if no selection-confirmation was given
  if myint == -1:
    return ''
  #Rewrite-Dialog
  myctitle = mystruct['title'][myint]
  mycmode = mystruct['mode'][myint]
  mycarg = mystruct['arg'][myint]
  #Rewrite carg with values to collect from dialog
  mycarg , mycvalid = rewritePathString(mycarg)
  #Exit if no confirmation was given
  os.system('logger sdfsdfsdf : -- '+mycmode+' '+mycarg+' done')
  if not mycvalid:
    os.system('logger invalide : -- '+mycmode+' '+mycarg+' done')
    return ''
  #Perform action
  if mycmode == 'run':
    #xbmc.executebuiltin('Notification(Executing,'+mycarg+')')
    os.system(mycarg+' &')
  elif mycmode == 'int':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin(mycarg)
  elif mycmode == 'cli':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    os.system('logger sysdfgdfg : -- '+mycarg+' done')
    xbmc.log('clirun '+mycarg)
    xbmc.executebuiltin('RunScript('+XBMCXIPATH+'/cliview.py,'+mycarg+')')
  elif mycmode == 'cmd':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    ok_cli_dialog(myctitle,mycarg)
  elif mycmode == 'txt':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin('RunScript('+XBMCXIPATH+'/textview.py,'+mycarg+')')
  elif mycmode == 'tail':
    #xbmc.executebuiltin('Notification(Executing,'+myctitle+')')
    xbmc.executebuiltin('RunScript('+XBMCXIPATH+'/tailview.py,'+mycarg+')')

maindlg(sys_argv[1])
