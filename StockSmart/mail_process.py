import time
import sys
import os, smtplib, mimetypes  
import socket

from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
from email.mime.multipart import MIMEMultipart  

MAIL_LIST = ["chen.tao.tommy@gmail.com"]  
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587 
MAIL_USER = 'tchen1973@gmail.com' 
MAIL_PASS = 'Happyday310'
MAIL_FROM = 'TCHEN1973<tchen1973@gmail.com>'

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
 
def send_mail(subject, content, filename = None):  
    print 'enter send mail.'
    try:  
        message = MIMEMultipart()  
        message.attach(MIMEText(content, 'plain'))  
        message.attach(MIMEText(html, 'html'))  
        message.attach(MIMEText(html_sign, 'html'))  
        message["Subject"] = subject  
        message["From"] = MAIL_FROM  
        message["To"] = ";".join(MAIL_LIST)
        message.preamble = 'You will not see this in a MIME-aware mail reader.\n'
          
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
        print "login."
        smtp.sendmail(MAIL_FROM, MAIL_LIST, message.as_string())  
        smtp.quit()  
        return True 
    except Exception, errmsg:  
        print "Send mail failed to: %s" % errmsg  
        return False 
 
if __name__ == "__main__":  
#   , r"G:\attachment.rar"): 
    if send_mail("subject", "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org", "readme.txt"):
        print "send mail OK."
    else:  
        print "send mail failed !"
