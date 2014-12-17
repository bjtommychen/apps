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
从yahoo读入股票到今天为止的历史数据csv文件
然后写入文件到目录history_data
'''

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

def yahoo_name_convert(code):
    if code.find('SH') != -1:
        new = code.replace('SH','') + '.ss'
    elif code.find('SZ') != -1:
        new = code.replace('SZ','') + '.sz'
    elif code.find('HK') != -1:
        new = code.replace('HK0','') + '.hk'
    else:
        new = code
    return new
    
def get_stock_history_csv(code, name):
    url = 'http://ichart.finance.yahoo.com/table.csv?s=' + yahoo_name_convert(code)+'&a=8&b=1&c=2014'
    local = 'history_data/'+str(code)+'.csv'
    if os.path.exists(local):
        print local, 'exist! skip!'
    else:  
        print 'Get stock_history_csv for', name, ', url:', url
        socket.setdefaulttimeout(4)
        try: 
            urllib.urlretrieve(url, local, 0)
        except:
            exit(1)
        print 'Got csv file, size:', os.path.getsize(local), 'bytes!'

def get_all_history():
    reader = csv.reader(file('stocklist_cn.csv','rb'))
    error_count = 0    
    for row in reader:
        code, name = row
        if code[0] == '6':
            codestr = 'SH' + code
        else:
            codestr = 'SZ' + code        
        try:
            get_stock_history_csv(codestr, name)
            error_count = 0
        except:
            print 'get_all_history error'
            error_count = error_count + 1
        if error_count > 10:
            print 'error count gt 10 ! exit !'
            break
    
if  __name__ == '__main__':
    print 'Start !'
    get_all_history()
    print 'Done !'
