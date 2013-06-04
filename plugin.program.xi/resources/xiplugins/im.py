#!/usr/bin/python
from os import path , getenv , system

OUR_CLIST = getenv('HOME') + '/.purple/spool/contacts_online'
OUR_XPLSDIR = getenv('HOME') + '/.local/xpls'

##
##base functions
##

#Read from file
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
  
def generate_xpls():
  myclist = file_read(OUR_CLIST)
  myout = '#icon=special://home/addons/plugin.program.xi/resources/skins/Default/media/chat.png\n'
  for myline in myclist.split('\n'):
    mysplit = myline.split(':',2)
    if len(mysplit) == 3:
      myproto = mysplit[0]
      myaddr = mysplit[1]
      myname = mysplit[2]
      myimg = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/proto-'+myproto+'.png'
      myudate = '1'
      #myuri = 'Notification(test,'+myname+')'
      myuri = 'RunScript(special://home/addons/plugin.program.xi/resources/scripts/sendim.py,'+myproto+':'+myaddr+')'
      myout += myudate+'\tim\t'+myname+'\t'+myuri+'\t'+myimg+'\n'
  return myout

def write_xpls():
 myxpls = generate_xpls()
 if not path.exists(OUR_XPLSDIR):
   system("mkdir -p '"+OUR_XPLSDIR+"'")
 file_write(OUR_XPLSDIR+'/im.xpls',myxpls)
 return OUR_XPLSDIR+'/im.xpls'

print write_xpls()

      