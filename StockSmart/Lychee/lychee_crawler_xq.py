﻿# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import re
import csv
from lychee_webdrv import *
import subprocess

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

start_time = time.time()
update_interval_in_seconds = 1800
heartbeat_interval_in_seconds = 3600
xq_hotlist_file = 'xq_hotlist_file.csv'
xq_url = 'http://xueqiu.com/hq'
xq_hotlist = []
run_1st = True
#wd = None
count = 100       # > heartbeat_interval_in_seconds to make it show when boot
    
def external_cmd(cmd, msg_in=''):
#    print cmd
#     return None, None
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        time.sleep(0.2)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None    
    
def crawler_geturl(url):
    #global wd
    #fp = open('xq.html', 'rb')
    #data = fp.read()
    #fp.close()
    #return data
    #if wd == None:
    wd = webdriver.Firefox()
    #wd = webdrv_get()
    wd.set_window_size(80,60)
    wd.get(url)
    if False:
        fp = open('xq.html', 'wb')
        fp.write(wd.page_source.encode('utf8')) 
        fp.close()
    else:
        data = wd.page_source.encode('utf8')
    # print parse_hotlist(data)
    wd.quit()
    return data

def crawler_geturl_phantomjs(url):
    # print url
    cmdline = 'phantomjs snap_webpage.js ' + url + ' capture.png > xq_hotlist.html'
    stdout_val, stderr_val = external_cmd(cmdline)
    fp = open('xq_hotlist.html', 'rb')
    data = fp.read()
    fp.close()
    print 'crawler_geturl_phantomjs got bytes:', len(data)
    return data
    
def parse_hotlist(data):   
    #if '热度排行榜' in data:
    #    print 'find !'
    pos1 = data.find(u'关注排行榜'.encode('utf8'))
    pos2 = data.find(u'讨论排行榜'.encode('utf8'))
    print pos1, pos2, len(data)
    if pos1 == -1 and pos2 == -1:
        return []
    data = data[pos1:pos2]
    # print data
    match = re.compile(r'(?<=target=["]_blank["] title=["]).*?(?=["])')  #for Chrome
    # match = re.compile(r'(?<=a title=["]).*?(?=["])')  #for Firefox
    r = re.findall(match, data)
    print type(r), len(r)
    # 去除列表中重复的元素
    sort_r = sorted(set(r),key=r.index)
    return sort_r
    
def crawler_xq_init():
    global xq_url
    global xq_hotlist_file
    global xq_hotlist
    print 'init'
    data = crawler_geturl_phantomjs(xq_url)
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
    
def crawler_init():
    banner = '*** Crawler Daemon. v1.0.2 '
    banner += '_xq_hotlist_'
    banner += '\n'
    return banner
    
def crawler_exit():
    return 'crawler_exit'
    
def crawler_xq_process(force = False):
    global xq_url
    global start_time
    global update_interval_in_seconds, heartbeat_interval_in_seconds, count
    global xq_hotlist
    global run_1st
    #debug
    #return ''
    
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
    strout = ''
    timetext = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
    data = crawler_geturl_phantomjs(xq_url)
    hotlist = parse_hotlist(data)
    if len(hotlist) == 0:
        strout += 'crawler GetHtml Failed!'
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
                strout += 'Newbie added:' + one + '\n' + timetext +'\n'
        if bNewbie:
            crawler_xq_savelist(hotlist)
            xq_hotlist = hotlist
        else:
            count += 1
            if count >= (heartbeat_interval_in_seconds/update_interval_in_seconds):
                count = 0
                strout += ' -------------XQ Hottlist ' + str(len(xq_hotlist)) +' No change ! phantomjs --------------\n' + timetext
            else:
                strout += ''
    return strout
   
if  __name__ == '__main__':
    if False:
        crawler_xq_init()
        data = crawler_geturl_request('http://www.xueqiu.com/hq')
        print len(data)
        fp = open('xq.html', 'wb')
        fp.write(data)
        fp.close()
        print parse_hotlist(data)
    elif False:
        fp = open('xq.html', 'rb')
        data=fp.read()
        fp.close()
        hotlist=parse_hotlist(data)
        for line in hotlist:
            wline = [line.decode('utf8').encode('gbk')]
            print repr(wline)
    if True:       
        crawler_xq_init()
        while True:
            strout = crawler_xq_process(True)
            if strout != '':
                print strout
            time.sleep(10)
    data = crawler_geturl_phantomjs(xq_url)
    hotlist = parse_hotlist(data)
    for one in hotlist:
        print one.encode('gbk')
