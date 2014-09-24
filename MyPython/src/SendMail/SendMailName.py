import time
import sys
import os, smtplib, mimetypes  
import socket

from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
from email.mime.multipart import MIMEMultipart  
from email.Header import Header   

reload(sys) 
sys.setdefaultencoding('gbk')

MAIL_LIST = ["tommy.chen@aa.com","chen.tao.tommy@aa.com"]  
MAIL_HOST = '10.10.0.0'
MAIL_PORT = 25
MAIL_USER = 'BEJBRS@aa.com' 
MAIL_PASS = 'pass'
MAIL_FROM = 'VSBJ ROBOT<BEJ.BRS@aa.com>'

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
    try_num = 3
    while(try_num):
        if send_mail_local(subject, content, flist):
            return True
        print 'send mail failed. try again!'
        time.sleep(5)
        try_num -= 1
    return False
  
def send_mail_local(subject, content, flist = None):  
    print 'start to send mail.'
    try:  
        message = MIMEMultipart()  
        message.attach(MIMEText(content, 'plain', 'utf-8'))  
#         message.attach(MIMEText(html, 'html'))  
#         message.attach(MIMEText(html_sign, 'html'))  
        message["Subject"] = Header(subject.decode('gbk'), 'utf-8')
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

def get_body(filename='body.txt'):
    body = 'Mail from Robot\n' 
    body += "Hi!\nCreate time: "+time.strftime("%Y%m%d-%H%M", time.localtime()) + '\n'
    body += 'Send Mail from ' + socket.gethostname() + ' under ' + os.getcwd() + '\n'
    body += '\n\n=========================== Main Text start ================================\n\n'
    print filename
    if os.path.exists(filename):
        f = open(filename)
        for line in f.readlines():
            body +=line
        f.close()
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
		bodytext = get_body()
    else:
		bodytext = get_body(sys.argv[2])
	
    if send_mail(sys.argv[1], bodytext, filelist):  
        print "send mail OK."
    else:  
        print "send mail failed !"
    pass