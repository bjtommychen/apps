
import time
import sys
import os, smtplib, mimetypes  
import socket

from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
from email.mime.multipart import MIMEMultipart  

MAIL_LIST = ["tommy.chen@verisilicon.com","chen.tao.tommy@gmail.com"]  
MAIL_HOST = '10.10.0.81'
MAIL_PORT = 25
MAIL_USER = 'BEJBRS@verisilicon.com' 
MAIL_PASS = 'Vs123456'
MAIL_FROM = 'VSBJ ROBOT<BEJ.BRS@verisilicon.com>'
#MAIL_FROM = 'tommy <tommy@bejn9014>'

html = """\
<html>
  <head></head>
  <body>
    <p>html, Hi!<br>
       How are you?<br>
       Here is the <a href="http://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
"""
html_sign = """\
    <b>Mail Send Easy version 2.0...</b>
    <p>Send Mail from <font size=+1>""" + socket.gethostname() + """</font> under <i> 
    """ + os.getcwd() +"""</i> </p>
    <b>End</b>
"""    

filelist = []

def send_mail(subject, content, flist):
    try_num = 2
    while(try_num):
        if send_mail_local(subject, content, flist):
            return True
        print 'send mail failed. try again!'
        try_num -= 1
    return False
  
def send_mail_local(subject, content, flist = None):  
    print 'start to send mail.'
    try:  
        message = MIMEMultipart()  
        message.attach(MIMEText(content, 'plain'))  
#         message.attach(MIMEText(html, 'html'))  
#         message.attach(MIMEText(html_sign, 'html'))  
        message["Subject"] = subject  
        message["From"] = MAIL_FROM  
        message["To"] = ";".join(MAIL_LIST)
        message.preamble = 'You will not see this in a MIME-aware mail reader.\n'
        
        for filename in flist:  
            if filename != None and os.path.exists(filename):  
                ctype, encoding = mimetypes.guess_type(filename)  
                if ctype is None or encoding is not None:  
                    ctype = "application/octet-stream" 
                maintype, subtype = ctype.split("/", 1)
                print 'attach maintype is', maintype  
                attachment = MIMEImage((lambda f: (f.read(), f.close()))(open(filename, "rb"))[0], _subtype = subtype)  
                attachment.add_header("Content-Disposition", "attachment", filename = filename)  
                message.attach(attachment)  
 
        print 'start to login...'
        smtp = smtplib.SMTP(MAIL_HOST, port=MAIL_PORT, timeout=20)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(MAIL_USER, MAIL_PASS)  
        print "login OK."
        smtp.sendmail(MAIL_FROM, MAIL_LIST, message.as_string())  
        smtp.quit()  
        return True 
    except Exception, errmsg:  
        print "Send mail failed to: %s" % errmsg  
        return False 

def get_body(filename):
    body = 'Mail from Robot\n' 
    body += "Hi!\nCreate time: "+time.strftime("%Y%m%d-%H%M", time.localtime()) + '\n'
    body += 'Send Mail from ' + socket.gethostname() + ' under ' + os.getcwd() + '\n'
    body += '\n\n=========================== Main Text start ================================\n\n'
    print filename
    f = open(filename)
    for line in f.readlines():
        body +=line
    return body

if __name__ == '__main__':
#     global filelist
#     print 'argv', len(sys.argv)
#     print sys.argv
    if len(sys.argv) < 2:
        print 'Example: \"Test Mail" body.txt attache.txt attach2.bin'
        exit(1)
    for i in range(3, len(sys.argv)):
        filelist.append(sys.argv[i])
    print filelist

    if len(sys.argv) < 3:
		bodytext = 'No Main Text.'
    else:
		bodytext = get_body(sys.argv[2])
	
    if send_mail(sys.argv[1], bodytext, filelist):  
        print "send mail OK."
    else:  
        print "send mail failed !"
    pass