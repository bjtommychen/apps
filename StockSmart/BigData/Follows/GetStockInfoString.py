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

'''
按照股票列表stocklist_cn.csv
从xueqiu读入股票信息, 现在重点是市值方面的
然后写入文件stockinfo_cn.csv
'''

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

DebugMode = False

def Float2Int_InString(str):
    # print str
    pos = str.find('.')
    if  pos == -1:
        return str
    else:
        rt = str[:pos]
        for i in range(pos + 1, len(str)):
            ch = str[i]
            # print 'NO.',i, ch
            if not ch.isdigit():
                rt += ch
        # print 'result:', rt
        return rt

#####################
######## CN #########
#####################
def get_StockInfo_cn(code):
    url = 'http://xueqiu.com/S/%s' % code
    # print url
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        data = r.content
        # print r.encoding
        r.close()
    except Exception, e:
        return 'Error'

    pos1 = data.find('span class="stockName"')        
    pos2 = data.find('</table>', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return 'Error'
    # print data[pos1:pos2].encode('gbk')
    match = re.compile(r'(?<=<span>).*?(?=<\/span>)')
    r = re.findall(match, data[pos1:pos2].encode('gbk'))
    if False:
        idx = 0
        print len(r), r
        for line in r:
            print idx, line.decode('gbk')
            idx += 1
    if len(r) < 19:
        if len(r) == 17:
            return r[6].decode('gbk')
        else:
            return 'Error'
    # 52周最高, 52周最低, 总市值, 每股净资产, 市盈率, 总股本, 每股收益, 市净率, 30日均量, 流通股本, 股息率, 市销率
    infoline = ''
    infoline += r[8].decode('gbk')
    return infoline    

def get_stock_infos_cn():
    global DebugMode
    fcsv = open('stockinfo_cn.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Code', 'Name', '总市值'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    
    count = 0
    reader = csv.reader(file('stocklist_cn.csv','rb')) 
    print 'Got list from csv'
    for one in reader:   
        code, name = one
        # print code, name
        if code[0] == '6':
            codestr = 'sh' + code
        else:
            codestr = 'sz' + code
        if (count%100 == 0):
            print codestr
            fcsv.flush()
        infostr = get_StockInfo_cn(codestr)
        infostr = Float2Int_InString(infostr)
        # print infostr
        # exit(0)
        if len(infostr) > 0:
            csvWriter.writerow([code, name, infostr.encode('gbk')])
        count += 1
        if DebugMode and count > 10:
            break                
 
    fcsv.close()    

#####################
######## HK #########
#####################    
def get_StockInfo_hk(code):
    url = 'http://xueqiu.com/S/%s' % code
    # print url
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        data = r.content
        # print r.encoding
        r.close()
    except Exception, e:
        return 'Error'

    pos1 = data.find('span class="stockName"')        
    pos2 = data.find('</table>', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return 'Error'
    # print data[pos1:pos2].encode('gbk')
    match = re.compile(r'(?<=<span>).*?(?=<\/span>)')
    r = re.findall(match, data[pos1:pos2].encode('gbk'))
    # print len(r), r
    # for line in r:
        # print line.decode('gbk')
    if len(r) < 19:
        return 'Error'
    # 52周最高, 52周最低, 总市值, 每股净资产, 市盈率, 总股本, 每股收益, 市净率, 30日均量, 流通股本, 股息率, 市销率
    infoline = ''
    infoline += r[8].decode('gbk')
    return infoline    
    
def get_stock_infos_hk():
    global DebugMode
    fcsv = open('stockinfo_hk.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Code', 'Name', '港股市值'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    
    count = 0
    reader = csv.reader(file('stocklist_hk.csv','rb')) 
    print 'Got list from csv'
    for one in reader:   
        code, name = one
        # print code, name
        codestr = code
        if (count%100 == 0):
            print codestr
            fcsv.flush()
        infostr = get_StockInfo_hk(codestr)
        infostr = Float2Int_InString(infostr)
        # print infostr
        # exit(0)
        if len(infostr) > 0:
            csvWriter.writerow([codestr, name, infostr.encode('gbk')])
        count += 1
        if DebugMode and count > 10:
            break                
 
    fcsv.close()        
    
#####################
######## US #########
#####################    
def get_StockInfo_us(code):
    url = 'http://xueqiu.com/S/%s' % code
    # print url
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        data = r.content
        # print r.encoding
        r.close()
    except Exception, e:
        return 'Error'

    pos1 = data.find('span class="stockName"')        
    pos2 = data.find('</table>', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return 'Error'
    # print data[pos1:pos2].encode('gbk')
    match = re.compile(r'(?<=<span>).*?(?=<\/span>)')
    r = re.findall(match, data[pos1:pos2].encode('gbk'))
    # print len(r), r
    # for line in r:
        # print line.decode('gbk')
    if len(r) < 19:
        return 'Error'
    # 52周最高, 52周最低, 总市值, 每股净资产, 市盈率, 总股本, 每股收益, 市净率, 30日均量, 流通股本, 股息率, 市销率
    infoline = ''
    infoline += r[8].decode('gbk')
    return infoline      
    
def get_stock_infos_us():
    global DebugMode
    fcsv = open('stockinfo_us.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Code', 'Name', '总市值'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    
    count = 0
    reader = csv.reader(file('stocklist_us.csv','rb')) 
    print 'Got list from csv'
    for one in reader:   
        code, name = one
        # print code, name
        codestr = code
        if (count%100 == 0):
            print codestr
            fcsv.flush()
        infostr = get_StockInfo_us(codestr)
        infostr = Float2Int_InString(infostr)
        # print infostr
        # exit(0)
        if len(infostr) > 0:
            csvWriter.writerow([codestr, name, infostr.encode('gbk')])
        count += 1
        if DebugMode and count > 10:
            break                
 
    fcsv.close()      
    
if  __name__ == '__main__':
    print 'Start !'    
    print Float2Int_InString(get_StockInfo_cn('sh600030'))
    print get_StockInfo_cn('sh600458')
    # print Float2Int_InString('123.456Wan')
    # get_stock_infos_cn()
    get_stock_infos_hk()
    get_stock_infos_us()    