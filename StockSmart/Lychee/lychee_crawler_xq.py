﻿# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import re
import csv

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

start_time = time.time()
update_interval_in_seconds = 300
xq_hotlist_file = 'xq_hotlist_file.csv'
xq_url = 'http://www.xueqiu.com/hq'
xq_hotlist = []
run_1st = True
    
def crawler_geturl(url):
    #fp = open('xq.html', 'rb')
    #data = fp.read()
    #fp.close()
    #return data
    c = webdriver.Firefox()
    c.set_window_size(80,60)
    c.get(url)
    if False:
        fp = open('xq.html', 'wb')
        fp.write(c.page_source.encode('utf8'))
        fp.close()
    else:
        data = c.page_source.encode('utf8')
    #print parse_hotlist(data)
    c.close()
    return data

def parse_hotlist(data):   
    #if '热度排行榜' in data:
    #    print 'find !'
    pos1 = data.find(u'关注排行榜'.encode('utf8'))
    pos2 = data.find(u'分享交易排行榜'.encode('utf8'))
    #print pos1, pos2, len(data)
    data = data[pos1:pos2]
    #print data
    #match = re.compile(r'(?<=target=["]_blank["] title=["]).*?(?=["])')  #for Chrome
    match = re.compile(r'(?<=a title=["]).*?(?=["])')  #for Firefox
    r = re.findall(match, data)
    print type(r), len(r)
    # 去除列表中重复的元素
    sort_r = sorted(set(r),key=r.index)
    #print sort_r
    return sort_r
    
def crawler_xq_init():
    global xq_url
    global xq_hotlist_file
    global xq_hotlist
    print 'init'
    data = crawler_geturl(xq_url)
    print 'get data', len(data)
    hotlist = parse_hotlist(data)            
    print len(hotlist)
    crawler_xq_savelist(hotlist) 
    print 'save done.'
    xq_hotlist = hotlist
    #print xq_hotlist

def crawler_xq_savelist(hotlist):
    print  'saving list to disk.'
    fcsv = open(xq_hotlist_file, 'wb')
    csvWriter = csv.writer(fcsv)
    for line in hotlist:
        # Notice below !!!
        wline = [line.decode('utf8').encode('gbk')]
        #print repr(wline)
        csvWriter.writerow(wline)
    fcsv.close()

def crawler_xq_loadlist():
    global xq_hotlist
    print  'loading list from disk.'
    reader = csv.reader(file(xq_hotlist_file,'rb'))
    hotlist = []
    for row in reader:
        #print type(row)
        hotlist.append(row[0].encode('utf'))
    print 'read', len(hotlist)
    return hotlist
    
def crawler_xq_process(force = False):
    global xq_url
    global start_time
    global update_interval_in_seconds
    global xq_hotlist
    global run_1st
    
    # because of codepage, sometimes load failed even on same system.
    if xq_hotlist == []: #not os.path.exists(xq_hotlist_file):
        crawler_xq_init()
    #elif xq_hotlist == []:
    #    xq_hotlist = crawler_xq_loadlist()
    #print xq_hotlist    
    # update ?
    if not run_1st:
        curr_time = time.time()
        if not force and (curr_time - start_time) < update_interval_in_seconds:    #update intervals
            return ''
        start_time = curr_time
    else:
	run_1st = False        
    # do
    # print xq_hotlist
    strout = '' #'--?--'
    data = crawler_geturl(xq_url)
    hotlist = parse_hotlist(data)
    if len(hotlist) == 0:
	str += 'GetHtml Failed!'
    else:
        #print 'got hotlist', len(hotlist), len(xq_hotlist)
        bNewbie = False
        for one in hotlist:
            #print 'checking', one, repr(one), repr(xq_hotlist[0])
            if len(xq_hotlist) == 0:
                bNewbie = True
                strout += 'strange: xq_hotlist empty !'
                break
            if one in xq_hotlist:
                continue
            else:
                bNewbie = True
                strout += 'Newbie added:' + one + '\n'
        if bNewbie:
            crawler_xq_savelist(hotlist)
        else:
            strout += ' ------------- No change ! --------------'
    return strout
   
if  __name__ == '__main__':
#    crawler_xq_init()
#    exit(0)	
#    crawler_geturl('http://www.xueqiu.com/hq')
#    fp = open('xq.html', 'rb')
#    data = fp.read()
#    fp.close()
#    print parse_hotlist(data)
    while True:
        strout = crawler_xq_process()
        if strout != '':
            print strout
        time.sleep(1)

