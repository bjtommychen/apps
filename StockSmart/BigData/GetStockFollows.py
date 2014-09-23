import time
import sys
import os
import socket
import math
import csv
import urllib2
import urllib
import string
import re
import csv
import requests

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

def convert_num(string):
    return str(string)

def get_StockFollows(code):
    url = 'http://xueqiu.com/S/%s/follows' % code
    # print url
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        data = r.content
        # print r.encoding
        r.close()
    except Exception, e:
        print 'Exception!'
        return []

    pos1 = data.find('div class="stockInfo"')        
    pos2 = data.find('div class="follower-list"', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return []
    data = data[pos1:pos2]    
    match = re.compile(r'(?<=a href=).*?(?=<\/a>)')
    r_name = re.findall(match, data.encode('gbk'))
    pos1 = r_name[0].find('>') 
    pos2 = r_name[0].find('(', pos1) 
    name = r_name[0][pos1+1:pos2]
    codename = r_name[0][pos2:]
    match = re.compile(r'(?<=<span>).*?(?=<\/span>)')
    r = re.findall(match, data.encode('gbk'))
    # print len(r), r
    pos1 = r[0].find('(')        
    pos2 = r[0].find(')', pos1)      
    if pos1 == -1 and pos2 == -1:
        return []
    return (name, codename, r[0][pos1+1:pos2])
        
def get_stock_follows():
    timetext = time.strftime("%Y-%m-%d-%H-%M", time.localtime()) 
    fcsv = open('stock_follows-'+timetext+'.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Name', '代码', '粉丝数'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    
    count = 0
    for code in (range(0, 4000) + range(300000, 301000)):
        codestr = 'sz' + "%06d" % int(code)
        if (code%100 == 0):
            print codestr
        infostr = get_StockFollows(codestr)
        if len(infostr) > 0:
            csvWriter.writerow(infostr)
        count += 1
        # if count > 10:
            # break    
    count = 0
    fcsv.flush()
    for code in range(600000, 605005):
        codestr = 'sh' + "%06d" % int(code)
        if (code%100 == 0):
            print codestr
        infostr = get_StockFollows(codestr)
        if len(infostr) > 0:
            csvWriter.writerow(infostr)
        count += 1
        # if count > 10:
            # break    
    fcsv.close()    
    
if  __name__ == '__main__':
    print 'Start !'
    # print get_StockFollows('sz002183')
    while True:
        time.sleep(1)
        get_stock_follows()
        print 'done.'
        time.sleep(3600)
    print 'Completed !'
    