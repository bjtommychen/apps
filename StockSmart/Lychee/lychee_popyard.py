# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
import re
import csv
import HTMLParser

from lychee_sendmail import *


print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

start_time = time.time()
update_interval_in_seconds = 1800
heartbeat_interval_in_seconds = 3600
urlText = []

class parseText(HTMLParser.HTMLParser):
    def handle_data(self, data):
        if data != '/n':
            # print [len], len(data), data
            urlText.append(data)

def popyard_getlist():
    data=urllib.urlopen("http://www.popyard.org").read()
    # print type(data), len(data)
    pos1 = data.find(u'中　国'.encode('gbk'))
    pos2 = data.find(u'国　际'.encode('gbk'))
    pos3 = data.find(u'科　教'.encode('gbk'))
    # print pos1, pos2, pos3
    match = re.compile(r'(?<=href=["]).*?(?=["])')
    data1=data[pos1:pos2]
    r = re.findall(match, data1)
    # print len(r), r
    list = r[1:]
    data2=data[pos2:pos3]
    r = re.findall(match, data2)
    # print len(r), r
    list += r[1:]
    # print len(list), list
    return list
    
def popyard_getone(url):
    global urlText
    title = ''
    # http://www.popyard.com/cgi-mod/newspage.cgi?num=1993025&r=0&v=0
    data=urllib.urlopen(url).read()    
    # print type(data), len(data)
    # Get Title
    match = re.compile(r'(?<=<TITLE>)\s*.*(?=<\/TITLE>)')
    r = re.findall(match, data)
    if len(r) > 0:
        title = r[0].decode('gbk')
        print 'TITLE: ', title
    # Get Text
    pos1 = data.find(u'服务使用须知'.encode('gbk'))
    pos1 = data.find('www.popyard.org', pos1)
    pos2 = data.find(u'【八阕】郑重声明'.encode('gbk'), pos1+100)
    # print pos1, pos2
    urlText = []
    lParser = parseText()
    lParser.feed(data[pos1:pos2])
    body = ''
    for line in urlText:
        body += line
        if len(line)>10:
            body += '\n'
    if False:
        fp = open('test.txt', 'w')
        fp.write(body)
        fp.close()
    else:    
        send_mail(title, body, [])

        
        
        
if  __name__ == '__main__':
    urllist = popyard_getlist()
    for url in urllist:
        popyard_getone(url)

