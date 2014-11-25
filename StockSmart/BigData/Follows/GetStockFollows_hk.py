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
import time

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

DebugMode = False
def convert_num(string):
    return str(string)

def get_StockFollows_HK(code):
    url = 'http://xueqiu.com/S/%s/follows' % code
    # print url
    # return []
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
    global DebugMode
    if os.environ.get('TOMMYDEBUG') == 'True':
        DebugMode = True
    timetext = time.strftime("%Y-%m-%d-%H-%M", time.localtime()) 
    fcsv = open('data/hk-'+timetext+'.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Name', '代码', '粉丝数'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    
    count = 0
    if True: # from list
        reader = csv.reader(file('stocklist_hk.csv','rb')) 
        print 'Got list from csv'
        for one in reader:   
            code, name = one
            # print code, name
            codestr = code
            if (count%100 == 0):
                print codestr
                fcsv.flush()
            infostr = get_StockFollows_HK(codestr)
            if len(infostr) > 0:
                csvWriter.writerow(infostr)
            count += 1
            if DebugMode and count > 10:
                break                
    else:
        for code in (range(1, 4000) + range(6800, 6900) + range(8000, 8400)):
            codestr = '' + "%05d" % int(code)
            if (code%10 == 0):
                print codestr
            infostr = get_StockFollows_HK(codestr)
            if len(infostr) > 0:
                csvWriter.writerow(infostr)
            count += 1
            if DebugMode and count > 10:
                break    
    fcsv.close()    
    
if  __name__ == '__main__':
    print 'Start !'
    print get_StockFollows_HK('00218')
    while True:
        time.sleep(1)
        get_stock_follows()
        print 'done.'
        break
        time.sleep(3600)
    print 'Completed !'
    