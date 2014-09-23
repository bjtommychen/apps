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

def get_StockInfo(code):
    url = 'http://xueqiu.com/S/%s' % code
    print url
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        data = r.content
        print r.encoding
        r.close()
    except Exception, e:
        return []

    pos1 = data.find('span class="stockName"')        
    pos2 = data.find('</table>', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return []
    # print data[pos1:pos2].encode('gbk')
    match = re.compile(r'(?<=<span>).*?(?=<\/span>)')
    r = re.findall(match, data[pos1:pos2].encode('gbk'))
    # print len(r), r
    # for line in r:
        # print line.decode('gbk')
    if len(r) < 19:
        return []
    # 52周最高, 52周最低, 总市值, 每股净资产, 市盈率, 总股本, 每股收益, 市净率, 30日均量, 流通股本, 股息率, 市销率
    infoline = []
    infoline.append(code)
    infoline.append(convert_num(r[3]))
    infoline.append(convert_num(r[5]))
    infoline.append(convert_num(r[8]))
    infoline.append(convert_num(r[9]))
    infoline.append(convert_num(r[10]))
    infoline.append(convert_num(r[12]))
    infoline.append(convert_num(r[13]))
    infoline.append(convert_num(r[14]))
    infoline.append(convert_num(r[15]))
    infoline.append(convert_num(r[16]))
    infoline.append(convert_num(r[17]))
    infoline.append(convert_num(r[18]))
    # print infoline
    return infoline

def get_stock_list():
    fcsv = open('stock_info.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Name','52周最高','52周最低','总市值','每股净资产','市盈率','总股本','每股收益','市净率',u'30日均量','流通股本','股息率','市销率'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    
    count = 0
    for code in (range(0, 4000) + range(300000, 301000)):
        if (code%100 == 0):
            print code
        codestr = 'sz' + "%06d" % int(code)
        infostr = get_StockInfo(codestr)
        if len(infostr) > 0:
            csvWriter.writerow(infostr)
        count += 1
        # if count > 10:
            # break    
    count = 0
    for code in range(600000, 605005):
        if (code%100 == 0):
            print code
        codestr = 'sh' + "%06d" % int(code)
        infostr = get_StockInfo(codestr)
        if len(infostr) > 0:
            csvWriter.writerow(infostr)
        count += 1

    fcsv.close()    
    

def convert_stock_list():
    reader = csv.reader(file('stock_info.csv','rb'))
    fcsv = open('stock_info_converted.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    i = 0
    for line in reader:
        if i==0:
            i+=1
            csvWriter.writerow(line)
            continue
        writeline = []
        for one in line:
            one = one.decode('gbk')
            if one.find(u'万') != -1 :
                one = one.replace(u'万', '')
            elif one.find(u'亿') != -1 :
                one = str(float(one.replace(u'亿', ''))*10000)
                # print type(one), one
            writeline.append(one)
        # print writeline
        csvWriter.writerow(writeline)
        i += 1
    fcsv.close()    

    
if  __name__ == '__main__':
    print 'Start !'
    # get_stock_list()
    convert_stock_list()
    print 'Completed !'
    