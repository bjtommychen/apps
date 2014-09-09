# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2

import re
import csv


print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

start_time = time.time()
update_interval_in_seconds = 1800
heartbeat_interval_in_seconds = 3600


def popy_getlist():
    data=urllib.urlopen("http://www.popyard.org").read()
    print type(data), len(data)
    pos1 = data.find(u'中　国'.encode('gbk'))
    pos2 = data.find(u'国　际'.encode('gbk'))
    pos3 = data.find(u'科　教'.encode('gbk'))
    print pos1, pos2, pos3
    match = re.compile(r'(?<=href=["]).*?(?=["])')
    data1=data[pos1:pos2]
    r = re.findall(match, data1)
    print len(r), r
    list = r[1:]
    data2=data[pos2:pos3]
    r = re.findall(match, data2)
    print len(r), r
    list += r[1:]
    print len(list), list
    
   
if  __name__ == '__main__':
    popy_getlist()

