#!/usr/bin/python
import email
import mailbox
from os import system , path , popen , getenv
from sys import argv

ourdir = '/var/lib/qvfs/mailfs/imap-fenner.info-qms/Mail'
ourdir = '/home/inf0rmix/QMail'
MAILDIR_PREFIX = getenv('HOME') + '/.local/mail'

##
## Base Functions
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

#Write file
def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

#Open system-command in a pipe and return data
def system_popen(cmd):
  mypipe = popen(cmd, 'r')
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

##Time Functions
from dateutil import parser
#Convet date-string to unix-time
def get_udate(mydatestr):
  #mydatestr='Mon, 18 Apr 2011 12:21:40 -0700'
  try:
    mydate = parser.parse(mydatestr)
  except:
    return '1'
  myudate=str(int(mydate.strftime("%s")))
  return myudate

##
##Main Functions
##

#Maildir fetcher using fetchmail
##
## Fetchmail Part
##

#Parse pop3(s)/imap(s) url and return config dict
def fetchmail_parse_cfgstr(mystr):
  myproto , myrest = mystr.split('://',1)
  myrest , myhost = myrest.rsplit('@',1)
  myuser , mypass = myrest.split(':')
  return myproto , myhost , myuser , mypass

#Parse pop3(s)/imap(s) url and return config dict
def fetchmail_parse_prepare(myicfg):
  myret = {}
  myret['id'] = myicfg['Id']
  myret['proto'] = myicfg['Proto']
  myret['host'] = myicfg['Host']
  myret['pass'] = myicfg['Pass']
  myret['user'] = myicfg['User']
  if myret['id'] == '':
    if myret['user'].find('@') > -1:
      myret['id'] = myret['user']
    else:
      myret['id'] = myret['proto'] + '-' + myret['host'] + '-' + myret['user']
  myret['maildir'] = MAILDIR_PREFIX + '/' + myret['id']
  myret['config'] = myret['maildir'] + '/.fetchmailrc'
  myret['cmd'] = 'LANG=C fetchmail -f ' + myret['config']
  myret['type'] = myret['proto'].rstrip('s')
  #myret['str'] = mystr
  #Config-Pipe
  myret['cfgline'] = 'poll ' + myret['host'] + ' protocol ' + myret['type']
  myret['cfgline'] += ' user "'  + myret['user'] + '" there with password "' + myret['pass'] + '" '
  #Pipe command
  myret['pipe'] = myret['cfgline'] + ' | fetchmail -f - '
  #Notify command
  myret['checkcmd'] = 'LANG=C fetchmail -c -N -f ' + myret['config']
  #Other vars
  if myicfg.has_key('SMTPHost'):
    myret['smtphost'] = myicfg['SMTPHost']
  #Validity
  if myret['type'] == 'pop3' or myret['type'] == 'imap':
    myret['valid'] = True
  else:
    myret['valid'] = False
  return myret

#Format fetchmailrc from config
def fetchmail_format_rc(mycfg):
  #defaults
  myret = 'set no syslog\nset daemon 0\n\n'
  myret += 'defaults:\n\n'
  myret += '\tkeep\n'
  myret += '\tno idle\n'
  #config
  myret += '\npoll ' + mycfg['host'] + ' protocol ' + mycfg['type'] + '\n'
  myret += 'user "'  + mycfg['user'] + '" there with password "' + mycfg['pass'] + '" '
  if mycfg['proto'] == 'pop3s' or mycfg['proto'] == 'imaps':
    myret += ' with options ssl sslcertpath '+mycfg['maildir']+' '
  myret += ';\n\n'
  myret += 'mda "/usr/bin/procmail -m '+mycfg['maildir']+'/.procmailrc"\n'
  return myret

def procmailrc_generate(mycfg):
  myout = 'MAILDIR='+mycfg['maildir']+'/\n'
  myout += 'DEFAULT=$MAILDIR\n'
  myout += 'SENDMAIL=/usr/bin/maildrop\n'
  myout += 'SENDMAILFLAGS=-d -M '+mycfg['maildir']+'/.maildroprc\n'
  return myout

def maildroprc_generate(mycfg):
  myout = 'MAILDIR='+mycfg['maildir']+'/\n'
  myout += '\n'
  return myout

def scriptgen_notify(mycfg):
  mychkscript = mycfg['maildir'] + '/check.sh'
  if not path.exists(mychkscript):
    mychkscriptsrc = '#!/bin/sh\n'
    mychkscriptsrc += 'MYMSG="$('+mycfg['checkcmd']+' 2>/dev/null)"\n'
    mychkscriptsrc += 'xbmc-send -a "Notification(Mails,$MYMSG)"\n'
    mychkscriptsrc += '\n'
    file_write(mychkscript,mychkscriptsrc)
    system("chmod +x '"+mychkscript+"'")


def get_msmtprc(myfrom,myhost,myuser,mypass):
  #Prepare config
  myout = 'defaults\n'
  myout += 'tls\ntls_certcheck off\n'
  myout += 'tls_trust_file /etc/ssl/certs/ca-certificates.crt\n'
  myout += '\n'
  myout += 'account default\n'
  myout += 'host ' + myhost + '\n'
  myout += 'from ' + myfrom + '\n'
  myout += 'auth on\n'
  myout += 'user ' + myuser + '\n'
  myout += 'password ' + mypass + '\n'
  myout += '\n'
  return myout

def get_muttrc(myfrom,myrcfile):
  #Prepare config
  myout = 'set sendmail="/usr/bin/msmtp -C ' + myrcfile + '\n'
  myout += 'from ' + myfrom + '\n'
  return myout

def smtpcfgen_do(mycfg):
  #Check for From-Address:
  if mycfg.has_key('From'):
    myfrom = mycfg['From']
  elif mycfg.has_key('id'):
    if mycfg['id'].find('@') > -1:
      myfrom = mycfg['id']
  elif mycfg.has_key('user'):
    if mycfg['user'].find('@') > -1:
      myfrom = mycfg['user']
  else:
    return 'error finding from-address'
  #Check for Host-Address:
  if mycfg.has_key('smtphost'):
    myhost = mycfg['smtphost']
  elif mycfg.has_key('host'):
    myhost = mycfg['host']
  else:
    return 'error finding host-address'
  #Check MSMTP+MUTT-config
  mymuttrc = mycfg['maildir'] + '/.muttrc'
  mymsmtprc = mycfg['maildir'] + '/.msmtprc'
  mysendsh = mycfg['maildir'] + '/sendtest.sh'
  if not path.exists(mymuttrc):
    mymuttconfig = get_muttrc(myfrom,mymsmtprc)
    file_write(mymuttrc, mymuttconfig )
  if not path.exists(mymsmtprc):
    mymsmtpconfig = get_msmtprc(myfrom,myhost,mycfg['user'],mycfg['pass'])
    file_write(mymsmtprc,mymsmtpconfig)
    system("chmod 600 '"+mymsmtprc+"'")
  if not path.exists(mysendsh):
    mysendshsrc = '#!/bin/bash\n'
    mysendshsrc += "echo Running as $USER @ `hostname -f` - Testing 1,2,3 ... | mutt -F '" + mymuttrc + "' -s \"XBMC-TestMail - $(date)\" " + myfrom + "\n"
    file_write(mysendsh,mysendshsrc)
    system("chmod +x '"+mysendsh+"'")
  return 'done'

def fetchmail_do(mycfg):
  #mycfg = fetchmail_parse_cfgstr(mycfgstr)
  #Generate MailDir
  if not path.isdir(mycfg['maildir']+'/new'):
    system("mkdir -p '"+mycfg['maildir']+"/new'")
  if not path.isdir(mycfg['maildir']+'/cur'):
    system("mkdir -p '"+mycfg['maildir']+"/cur'")
  #Check Procmailrc
  myprocmailrc = mycfg['maildir'] + '/.procmailrc'
  if not path.exists(myprocmailrc):
    file_write(myprocmailrc,procmailrc_generate(mycfg))
    system("chmod 600 '"+myprocmailrc+"'")
  #Check Maildroprc
  mymaildroprc = mycfg['maildir'] + '/.maildroprc'
  if not path.exists(mymaildroprc):
    file_write(mymaildroprc,maildroprc_generate(mycfg))
    system("chmod 600 '"+mymaildroprc+"'")
  #Generate/Write fetchmailrc
  myfetchmailrc = mycfg['maildir'] + '/.fetchmailrc'
  if not path.exists(myfetchmailrc):
    file_write(myfetchmailrc,fetchmail_format_rc(mycfg))
    system("chmod 600 '"+myfetchmailrc+"'")
  #Generate update-script
  myuscript = mycfg['maildir'] + '/update.sh'
  if not path.exists(myuscript):
    myuscriptsrc = '#!/bin/sh\n'
    myuscriptsrc += mycfg['cmd']+' >/dev/null 2>&1\n'
    myuscriptsrc += 'rm '+mycfg['maildir']+'/index.xpls >/dev/null 2>&1\n'
    myuscriptsrc += 'xbmc-send -a Container.Refresh >/dev/null 2>&1\n'
    file_write(myuscript,myuscriptsrc)
    system("chmod +x '"+myuscript+"'")
  #Generate check-script
  scriptgen_notify(mycfg)
  #Check for ssl-certificate
  if mycfg['proto'] == 'imaps':
    myscert = mycfg['maildir'] + '/' + mycfg['host'] + '.pem'
    if not path.exists(myscert):
      mycdata = get_ssl_cert(mycfg['host'],'993')
      file_write(myscert,mycdata)
      system("c_rehash '"+mycfg['maildir']+"'")
  elif mycfg['proto'] == 'pop3s':
    myscert = mycfg['maildir'] + '/' + mycfg['host'] + '.pem'
    if not path.exists(myscert):
      mycdata = get_ssl_cert(mycfg['host'],'995')
      file_write(myscert,mycdata)
      system("c_rehash '"+mycfg['maildir']+"'")
  return mycfg

def get_ssl_cert(myhost,myport):
  mycrtdata = system_popen("echo quit | openssl s_client -connect "+myhost+":"+myport+" -showcerts 2>/dev/null | sed -ne '/BEGIN/,/END/p'")
  return mycrtdata # .rstrip('\n')

#Maildir parser

def parse_email_headinfo(mymailfile):
  myhdata = {'from':'','date':'','udate':'','subject':'','to':''}
  myhdata['file'] = mymailfile
  myhdata['valid'] = '0'
  mycnt = 0
  try:
    myfh = open(mymailfile)
  except:
    return myhdata
  while 1:
      myline = myfh.readline()
      if not myline:
	  return myhdata
      if myline.find(': ') > -1:
	myval = myline.strip('\n\r\t').split(': ',1)[1]
	if myline.startswith('From: ') and myhdata['from'] == '':
	  myhdata['valid'] = '1'
	  myhdata['from-name'] = myval
	  myhdata['from'] = parse_email_addresses(myval)
	  mycnt += 1
	elif myline.startswith('To: ') and myhdata['to'] == '':
	  myhdata['to'] = myval
	  mycnt += 1
	elif myline.startswith('Date: ') and myhdata['date'] == '':
	  myhdata['date'] = myval
	  myhdata['udate'] = get_udate(myval) # TODO
	  mycnt += 1
	elif myline.startswith('Subject: ') and myhdata['subject'] == '':
	  myhdata['subject'] = myval
	  mycnt += 1
	#Exit if we have all possible head-elements
	if mycnt >= 4:
	  return myhdata
  return myhdata

#Get first email address out of a list of strings
def parse_email_addresses(mymsg):
  myheadstr=str(mymsg).replace('"','').replace("'",'').replace("<",'').replace(">",'')
  if myheadstr.count(' ') == 0:
    if myheadstr.find('@') > -1:
      return myheadstr
  for myaddr in myheadstr.split(' '):
    if myaddr.find('@') > -1:
      return myaddr
  return ''

def format_line(myhi):
  #myuri='Notification(mailfrom,'+myhi['from']+')'
  myuri='RunScript(special://home/addons/plugin.program.xi/resources/scripts/mailview.py,'+myhi['file']+')'
  mythumb = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/mail.png'
  myline = myhi['udate']+'\tmail\t'+myhi['subject']+'\t'+myuri+'\t'+mythumb+'\n'
  return myline

def parse_maildir(mydir):
  md = mailbox.Maildir(mydir)
  myroot = md.get_folder('')
  myitems = myroot.items()
  myout = ''
  for myitem in myitems:
    myitemkey = myitem[0]
    if myroot._toc.has_key(myitemkey):
      mymailfile = mydir + '/' + myroot._toc[myitemkey]
    else:
      mymailfile = '/dev/null'
    myheadinfo = parse_email_headinfo(mymailfile)
    myout += format_line(myheadinfo)
    #print myroot.get_message(myitem[0])
  return myout.rstrip('\n')

##XDG-Parser  
def parse_xdg_file(myfile):
  mytmpcfg = {}
  for myline in file_read(myfile).split('\n'):
    mysplit = myline.split('=',1)
    if len(mysplit) == 2:
      mytmpcfg[mysplit[0]] = mysplit[1]
  #Convert url to protocol/id
  if mytmpcfg.has_key('URL'):
    if mytmpcfg['URL'].find('://') > -1:
      myproto , myid = mytmpcfg['URL'].split('://',1)
      mytmpcfg['Proto'] , mytmpcfg['Id'] = myproto , myid
      #mytmpcfg['Proto'] , mytmpcfg['Id'] = myproto , myid.replace('@','-')
  else:
    mytmpcfg['Proto'] , mytmpcfg['Id'] = '' , ''
  return mytmpcfg

#Parse XDG-File , Return internal-config , Fetch mail if config was generated
def get_maildir_from_xdg(mycfile):
  myxcfg = parse_xdg_file(mycfile)
  myadvcfg = fetchmail_parse_prepare(myxcfg)
  myfcfg = fetchmail_do(myadvcfg)
  myscfg = smtpcfgen_do(myadvcfg)
  return myfcfg

#Get addons for xpls
def get_xpls_extitems(mycfg):
  myout = ''
  #Fetch action
  myuri = 'RunScript(special://home/addons/plugin.program.xi/run.py,exec?'+mycfg['maildir']+'/update.sh)'
  mythumb = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/mail-receive.png'
  myudate , mymode , mytext = '1' , 'xbmc' , 'Fetch mails...'
  myout += myudate + '\t' + mymode + '\t' + mytext + '\t' + myuri + '\t' + mythumb + '\n'
  #SendMail-Test action
  myuri = 'RunScript(special://home/addons/plugin.program.xi/run.py,exec?'+mycfg['maildir']+'/sendtest.sh)'
  mythumb = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/mail.png'
  myudate , mymode , mytext = '1' , 'xbmc' , 'Send testmail to mailbox...'
  myout += myudate + '\t' + mymode + '\t' + mytext + '\t' + myuri + '\t' + mythumb + '\n'
  #Check action
  myuri = 'RunScript(special://home/addons/plugin.program.xi/run.py,exec?'+mycfg['maildir']+'/check.sh)'
  mythumb = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/refresh.png'
  myudate , mymode , mytext = '1' , 'xbmc' , 'Check for new mails...'
  myout += myudate + '\t' + mymode + '\t' + mytext + '\t' + myuri + '\t' + mythumb + '\n'
  return myout

#Get full xplaylist
def get_xpls(mycfile):
  mycfg = get_maildir_from_xdg(mycfile)
  myicon = 'special://home/addons/plugin.program.xi/resources/skins/Default/media/mail.png'
  myout = '#icon='+myicon+'\n'
  myout += get_xpls_extitems(mycfg)
  myout += parse_maildir(mycfg['maildir'])
  #write to local maildir
  file_write(mycfg['maildir']+'/index.xpls',myout)
  return mycfg['maildir']+'/index.xpls'

##
## Main
##

#opt s out-file
def main_action(myarg,myopt=''):
  if path.isdir(myarg):
    return parse_maildir(myarg)
  elif path.exists(myarg):
    myrealxpls = get_xpls(myarg)
    if myopt == '-p':
      return myrealxpls.rstrip('\n')
    elif myopt != '':
      system("ln -s -f '"+myrealxpls+"' '"+myopt+"'")
  else:
    return 'TODO: default mode'

#mycfgdata = fetchmail_do('imaps://mafenner@gmail.com:23chick@imap.googlemail.com')
#print mycfgdata

#print parse_maildir('/home/inf0rmix/.local/mail/imaps-imap.googlemail.com-mafenner_gmail.com')
#system('logger -- a')
if len(argv) == 2:
  main_action(argv[1])
else:
  if argv[1] == '-p':
    print main_action(argv[2],'-p') 
  else:
    main_action(argv[1],argv[2]) #TODO: print xpls only mode
#system('logger -- b')