# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import re
import csv

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('gbk')

start_time = time.time()
xq_hotlist_file = 'xq_hotlist_file.csv'

def crawler_geturl(url):
    c = webdriver.Chrome()
    c.set_window_size(0,0)
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
    if '热度排行榜' in data:
        print 'find !'
    pos1 = data.find(u'关注排行榜'.encode('utf8'))
    pos2 = data.find(u'分享交易排行榜'.encode('utf8'))
    print pos1, pos2, len(data)
    data = data[pos1:pos2]
    match = re.compile(r'(?<=target=["]_blank["] title=["]).*?(?=["])')
    r = re.findall(match, data)
    print type(r), len(r)
    hotlist = []
    fcsv = open(xq_hotlist_file, 'wb')
    csvWriter = csv.writer(fcsv)
    print r
    for line in r:
        print line
        print line.decode('utf8').encode('gbk')
        csvWriter.writerow(line.decode('utf8').encode('gbk'))
        #print type(line), type(line.decode('utf8'))
        #wline = line.encode('gbk')
        #print wline
        #csvWriter.writerow(wline)        
        wline = line.decode('utf8').encode('gbk')
        print wline
        #print wline, str(wline).encode('gbk')
        csvWriter.writerow(wline)
        #wline = line.decode('utf8').encode('gbk')
        #csvWriter.writerow(wline)
        #hotlist.append(line.decode('utf8'))
        #hotlist.append(line.decode('utf8').encode('gbk'))
        #print line.decode('utf8')
    fcsv.close()
    return hotlist


    
def crawler_xq_process():
    url = 'http://www.xueqiu.com/hq'
    if True:
        fp = open('xq.html', 'rb')
        data = fp.read()
        fp.close()    
    else:
        data = crawler_geturl(url)
    hotlist = parse_hotlist(data)
    print hotlist
   
if  __name__ == '__main__':
#    crawler_geturl('http://www.xueqiu.com/hq')
#    fp = open('xq.html', 'rb')
#    data = fp.read()
#    fp.close()
#    print parse_hotlist(data)
    crawler_xq_process()

