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
update_interval_in_seconds = 3600
heartbeat_interval_in_seconds = 3600
run_1st = True

urlText = []
title = ''
body = ''
oldlist = []

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
    
def popyard_get_next(url):
    global urlText
    text = '\n-------------------------\n'
    data=urllib.urlopen(url).read()    
    # Get Text
    pos1 = data.find(u'服务使用须知'.encode('gbk'))
    pos1 = data.find('www.popyard.org', pos1)
    pos2 = data.find(u'【八阕】郑重声明'.encode('gbk'), pos1+100)
    urlText = []
    lParser = parseText()
    lParser.feed(data[pos1:pos2])
    for line in urlText:
        text += line
        if len(line)>10:
            text += '\n'    
    return text
    
def popyard_getone(url):
    global urlText
    global title
    global body
    title = ''
    
    print url
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
    
    pos4 = data.find(u'| 共 '.encode('gbk'), pos1)
    match = re.compile(r'(?<=<a href=).*?(?=>)')
    r = re.findall(match, data[pos4:pos2])
       
    # print pos1, pos2
    urlText = []
    lParser = parseText()
    lParser.feed(data[pos1:pos2])
    body = ''
    for line in urlText:
        body += line
        if len(line)>10:
            body += '\n'

    if len(r) > 0:
        baseright = url.rfind('/')
        base = url[:baseright+1]
        for one in r:
            print '-------' + base + one
            body += popyard_get_next(base+one)
            
    if True:
        fp = open('test.txt', 'w')
        fp.write(body)
        fp.close()
    if True:    
        send_mail(title, body, [])
     
def popyard_process(force = False):     
    global run_1st
    global start_time
    global update_interval_in_seconds, heartbeat_interval_in_seconds, count
    global oldlist

    if not run_1st:
        curr_time = time.time()
        if not force and (curr_time - start_time) < update_interval_in_seconds:    #update intervals
            return ''
        start_time = curr_time
    else:
        run_1st = False        
    # main work
    newlist = popyard_getlist()
    for newone in newlist:
        if newone in oldlist:
            print 'Skip ' + newone
        else:
            popyard_getone(newone)
    oldlist = []
    for newone in newlist:
        oldlist.append(newone)
    print 'Done!'
        
if  __name__ == '__main__':
    # urllist = popyard_getlist()
    # for url in urllist:
        # popyard_getone(url)
    # popyard_getone('http://www.popyard.com/cgi-mod/newspage.cgi?num=1993025&r=0&v=0')
    if True:            
        while True:
            strout = popyard_process()
            if strout != '':
                print strout
            time.sleep(60)
