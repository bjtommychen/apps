import sys
import os
import socket
import math
import csv
import stat,fnmatch
import struct
import urllib, urllib2
import string
import re
import requests

def get_StockList_cn():
    ### Get Data ###
    url = 'http://quote.eastmoney.com/stocklist.html'
    if True:   # Set True to get webpage, False to get data from File.
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
            r = requests.get(url,timeout=5,headers=headers)
            data = r.content
            print r.encoding
            r.close()
            if True: # set True to save data for later use.
                fp = open("getstocklist.html", 'wb');
                fp.write(data)
                fp.close()
        except Exception, e:
            return 'Error'
    else:
        fp = open("getstocklist.html", 'rb');
        data = fp.read()
        fp.close()
        print 'get data from getstocklist.html ', len(data), 'bytes.'
    ### Process List ###
    match = re.compile(r'(?<=<li>).*?(?=<\/li>)')
    r = re.findall(match, data)
    print len(r)
    list=[]
    for one in r:
        pos1 = one.find('>')
        pos2 = one.rfind('<')
        one = one[pos1+1:pos2]
        name = one[:one.find('(')]
        code = one[one.find('('):].replace('(','').replace(')','')
        if len(code) != 6:
            continue
        line = code, name
        if code[0] == '0' or code[0] == '3' or code[0] == '6':
            # print line
            list.append(line)
    # print len(list),list                
    print 'get stock total', len(list)
    fcsv = open('stocklist_cn.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    for line in list:
        csvWriter.writerow(line)
    fcsv.close()  
    
def get_StockList_hk():
    ### Get Data ###
    url = 'http://quote.eastmoney.com/hk/HStock_list.html'
    if True:   # Set True to get webpage, False to get data from File.
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
            r = requests.get(url,timeout=5,headers=headers)
            data = r.content
            print r.encoding
            r.close()
            if True: # set True to save data for later use.
                fp = open("getstocklist.html", 'wb');
                fp.write(data)
                fp.close()
        except Exception, e:
            return 'Error'
    else:
        fp = open("getstocklist.html", 'rb');
        data = fp.read()
        fp.close()
        print 'get data from getstocklist.html ', len(data), 'bytes.'
    ### Process List ###
    match = re.compile(r'(?<=<li>).*?(?=<\/li>)')
    r = re.findall(match, data)
    print len(r)
    # print r
    list=[]
    for one in r:
        pos1 = one.find('>')
        pos2 = one.rfind('<')
        # print one
        one = one[pos1+1:pos2]
        name = one[one.find(')')+1:]
        code = one[:one.find(')')].replace('(','').replace(')','')
        # if len(code) != 6:
            # continue
        line = code, name
        # print one, line
        if len(code) > 0 and code[0] == '0':# or code[0] == '3' or code[0] == '6':
            # print code, name
            list.append(line)
    # print len(list),list                
    print 'get stock total', len(list)
    fcsv = open('stocklist_hk.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    for line in list:
        csvWriter.writerow(line)
    fcsv.close()  

def get_StockList_us():
    ### Get Data ###
    url = 'http://vip.stock.finance.sina.com.cn/usstock/ustotal.php'
    if True:   # Set True to get webpage, False to get data from File.
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
            r = requests.get(url,timeout=5,headers=headers)
            data = r.content
            print r.encoding
            r.close()
            if True: # set True to save data for later use.
                fp = open("getstocklist.html", 'wb');
                fp.write(data)
                fp.close()
        except Exception, e:
            return 'Error'
    else:
        fp = open("getstocklist.html", 'rb');
        data = fp.read()
        fp.close()
        print 'get data from getstocklist.html ', len(data), 'bytes.'
    ### Process List ###
    match = re.compile(r'.*?(?=<\/a>)')
    r = re.findall(match, data)
    print len(r)
    list=[]
    for one in r:
        pos1 = one.find('>')
        pos2 = one.rfind('<')
        # print one
        one = one[pos1+1:pos2]
        # print one
        name = one[:one.find('(')]
        code = one[one.find('('):].replace('(','').replace(')','')
        code = code.strip()
        if len(code) == 0:
            continue
        line = code, name
        # print '[',code, ']', name
        if len(code) > 0 and code[0].isalpha() and name.find('ETF')==-1:
            # print '[',code, ']', name
            list.append(line)
    # print len(list),list                
    print 'get stock total', len(list)
    fcsv = open('stocklist_us.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    for line in list:
        csvWriter.writerow(line)
    fcsv.close()  
    
######################################################
if  __name__ == '__main__':
    print 'Start !'
    print '*** get_StockList_cn ***'
    get_StockList_cn()
    print '*** get_StockList_cn ***'
    get_StockList_hk()
    print '*** get_StockList_us ***'
    get_StockList_us()
    print 'Completed !'        
        