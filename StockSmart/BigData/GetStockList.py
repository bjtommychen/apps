import time
import sys
import os
import socket
import math
import csv
import urllib2
import urllib
import string

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
# sys.setdefaultencoding('utf8')
sys.setdefaultencoding('gbk')

def get_rt_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
#     print url
    try:
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
    except Exception, e:
        return ('', 0., 0, 0., 0, 0)
    else:
        strs = content.decode('gbk')
        data = strs.split('"')[1].split(',')
#         print data
        name = "%s" % data[0]
        if (name):
            return (name, "%-5s" % float(data[1]), "%-5s" % float(data[2]), "%-5s" % float(data[3]), 
                    "%-5s" % float(data[4]), "%-5s" % float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)

def get_sh_list():
    fcsv = open('sh_list.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    
    for code in range(600000, 605005):
        if (code%100 == 0):
            print code
#         codestr = ''
        codestr = 'sh' + "%06d" % int(code)
#         print codestr
#         name, price_current, price_diff, change_percent = get_price(codestr)
        name, openprice, lastclose, curr, todayhigh, todaylow = get_rt_price(codestr)
        if (name):
            name = string.replace(name,' ','')
            line = codestr, name
#             print line
            csvWriter.writerow(line)
    fcsv.close()
    
def get_sz_list():
    fcsv = open('sz_list.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    
    for code in range(0, 4000):
        if (code%100 == 0):
            print code
        codestr = 'sz' + "%06d" % int(code)
#         print codestr, code
#         continue
        name, openprice, lastclose, curr, todayhigh, todaylow = get_rt_price(codestr)
        if (name):
            name = string.replace(name,' ','')
            line = codestr, name
            csvWriter.writerow(line)

    for code in range(300000, 301000):
        if (code%100 == 0):
            print code
        codestr = 'sz' + "%06d" % int(code)
        name, openprice, lastclose, curr, todayhigh, todaylow = get_rt_price(codestr)
        if (name):
            name = string.replace(name,' ','')
            line = codestr, name
            csvWriter.writerow(line)    
    fcsv.close()    
    
if  __name__ == '__main__':
    print 'Start !'
    get_sh_list()
    get_sz_list()
    print 'Completed !'
    