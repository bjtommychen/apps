﻿import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import struct
from pandas import DataFrame, Series
import pandas as pd
import urllib, urllib2
import string
import re
import requests

from ParseWebPrice import *

reload(sys) 
sys.setdefaultencoding('utf')

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
#            print fullname
            st = os.lstat(fullname)
            if stat.S_ISDIR(st.st_mode) and subdir:
                dirlist += getFileList(fullname,ext)
            elif os.path.isfile(fullname):
                if fnmatch.fnmatch( fullname, ext): 
                    dirlist.append(fullname)
                else:
                    pass
        return dirlist
    else:
        return [] 
        
def GetFollowsChanges_InFileList(filelist):
    init_run = True
    for filepath in filelist:
        print filepath
        df = pd.read_csv(filepath, names = ['name', 'code', 'follows'], skiprows=[0])
        if init_run:
            df2 = df.copy()
            init_run=False
        else:
            # print df.head(5)
            chg = 0
            j_start = 0
            for i in xrange(len(df)):
                for j in xrange(j_start, len(df2)):
                    if df['name'][i] == df2['name'][j]:
                        follow_chg = df2['follows'][j] - df['follows'][i]
                        chg += abs(follow_chg)
                        j_start = j
                        break
                        # print i, j, '%10s'%df['name'][i], follow_chg
            print 'chg', chg
            df2 = df.copy()

def GetFollowChangesByName_Assembled(list, name, startidx = 0):
    # print len(list)
    ff = []
    lastone = 0
    for i in xrange(0, len(list)):
        df = list[i]
        for j in xrange(0, len(df)):
            if df['code'][j] != name:
                continue
            lastone = df['follows'][j]
            ff.append(lastone)
            # print j, lastone
            break
        if j == len(df)-1:
            ff.append(lastone)
    # print len(ff),ff
    if len(ff) != len(list):
        print len(ff), len(list)
        exit(0)
    ff_chg = []
    for i in range(0, len(ff)-1):
        ff_chg.append(ff[i]-ff[i+1])
    return ff_chg
    
def GetFollowChangesByName(df1, df2, name, startidx = 0):
    # if startidx > 10:
        # startidx -= 10
    # print startidx
    range = 50
    for i in xrange(startidx, len(df1)):
        if df1['code'][i] != name:
            continue
        # try fast mode first.
        if startidx > range:
            startidx -= range
        for j in xrange(startidx, min(startidx+range*2, len(df2))):
            if name == df2['code'][j]:
                follow_chg = df1['follows'][i] - df2['follows'][j]
                # print type(follow_chg)
                return follow_chg, j
        # use normal way
        for j in xrange(0, len(df2)):
            if name == df2['code'][j]:
                follow_chg = df1['follows'][i] - df2['follows'][j]
                return follow_chg, j
        break        
                
    return 0, 0

    
def GetStockInfo_fromFile(reader, check_code):
    # name = name.replace('(','').replace(')','').replace(':','').lower()
    # check_code = check_code[2:]
    # print check_code
    for one in reader:
        # print one, code
        code, name, info = one
        # print code,check_code
        if code == check_code:
            return info
    return 'N/A'
    
def CheckStar(name, code, chg_p1, pct_chg, chg_p2, chg_p3, LiuTongYi):
    # print type(pct_chg), pct_chg, chg_p1, LiuTongYi
    if chg_p1 > 10 and pct_chg > 1.0:# and LiuTongYi < 80:
        return True
    else:
        return False

# SINA API FOR HK, DELAY 15MIN        
def get_hk_rt_price_sinaapi(code='hk00390'):
    code = 'hk'+code
    url = 'http://hq.sinajs.cn/?list=%s' % code
    # print url
    try:
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
    except Exception, e:
        return ('', 0, 0, 0, 0, 0) 
    else:
        strs = content.decode('gbk')
        data = strs.split('"')[1].split(',')
        # print data
        name = "%s" % data[0]
        name = string.replace(name,' ','')
        if (name):
            return (name, float(data[1+1]), float(data[2+1]), float(data[3+1]), 
                     float(data[4+1]), float(data[5+1]))
        else:
            return ('', 0, 0, 0, 0, 0)

def get_hkstock_rt_price(code='hk00390'):
    code = code.replace('(','').replace(')','').upper()
    code = code.replace(':','').replace('HK0','') 
    if len(code) == 4:
        code = '0'+code
    # print code
    if False:
        return get_hk_rt_price_sinaapi(code)
    else:
        return get_hk_rt_price(code)
            
us_url_swap = 1            
def get_us_rt_price_yahoo(code):    # DELAY 15 MINUTES
    global us_url_swap
    code = code.replace('(','').replace(')','').upper()
    code = code.replace(':','').replace('HK0','') + '.hk'
    # print code
    if us_url_swap == 1:
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=nopl1hg' % code
    else:
        url = 'http://quote.yahoo.com/d/quotes.csv?s=%s&f=nopl1hg' % code
    us_url_swap = (us_url_swap+1)%2
    # print url
    try:
        sock = urllib.urlopen(url)
        strs = sock.readline()
        sock.close()
        if 'strict' in strs:
            return ('', 0, 0, 0, 0, 0) 
    except Exception, e:
        return ('', 0, 0, 0, 0, 0) 
    else:
        strs = string.replace(strs,'\r\n','')
        data = strs.split('"')[2].split(',')
        name = strs.split('"')[1]
        if (name):
            return (name, float(data[1]), float(data[2]), float(data[3]), 
                     float(data[4]), float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)    
            
def get_stock_lastday_status(code):
    # return 0, 0, 0
    rt = get_hkstock_rt_price(code)
    if rt == []:
        rt = get_hkstock_rt_price(code)
        if rt == []:
            return 0,0,'%Error'
    name, openprice, lastclose, curr, todayhigh, todaylow = rt
    diff_pct = '%Error'
    if lastclose != 0:
        diff_pct = str(round(((curr - lastclose)*100/lastclose), 2))+'%'
    return lastclose, curr, diff_pct    
        
def GetFollowsByCode(df1, code, startidx = 0):
    codemarket = 0 
    if startidx > 10:
        startidx -= 10
    # print code
    if codemarket == 2:
        code2 = code
        # print code2
        for i in xrange(startidx, len(df1)):
            if df1['code'][i].find(code2) == -1:
                continue
            return df1['name'][i], df1['follows'][i]
    else:
        # code2 = '('+code[:2]+':'+code[2:]+')'
        code2 = code
        # print code2
        for i in xrange(startidx, len(df1)):
            if df1['code'][i] != code2:
                continue
            return df1['name'][i], df1['follows'][i]
    return '',0  
        
def GetFollowsMeanByCode(dirfilelist, code = '(SH:600036)'):
    follows_chg_list = []
    last_follows = 0
    for one in dirfilelist:
        # print one
        df_curr = pd.read_csv(one, names = ['name', 'code', 'follows'], skiprows=[0])
        name, follows = GetFollowsByCode(df_curr, code)
        if follows > 0:
            if last_follows == 0:
                last_follows = follows
            else:
                diff = abs(follows - last_follows)
                last_follows = follows
                follows_chg_list.append(diff)
    # print follows_chg_list
    df = Series(follows_chg_list)
    # print df.mean()   
    return (df.mean())
def GetFollowsChanges_InRecentFiles(rawlist):
    dirfilelist = []
    for one in rawlist:
        if 'hk-' in one:
            dirfilelist.append(one)
            
    filelist = dirfilelist[-8:]
    # print filelist
    dfp7 = pd.read_csv(filelist[0], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp6 = pd.read_csv(filelist[1], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp5 = pd.read_csv(filelist[2], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp4 = pd.read_csv(filelist[3], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp3 = pd.read_csv(filelist[4], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp2 = pd.read_csv(filelist[5], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp1 = pd.read_csv(filelist[6], names = ['name', 'code', 'follows'], skiprows=[0])
    df   = pd.read_csv(filelist[7], names = ['name', 'code', 'follows'], skiprows=[0])
    # df_stockinfo   = pd.read_csv('stock_info_converted.csv', names = ['A','B','C','D','E','F','G','H','I','J','K','L','M'], skiprows=[0])

    list = []
    for i in xrange(len(df)):
        if i%100 == 0:
            print '.',
        name = df['name'][i]
        code = df['code'][i]
        xq_code = code[code.find(':'):].replace('(','').replace(')','').replace(':','').upper()
        # print name, code, GetStockInfo_fromFile(csv.reader(file('stockinfo_hk.csv','rb')),xq_code)
        follows = df['follows'][i]
        if False:
            chg_p1, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7 = GetFollowChangesByName_Assembled([df,dfp1, dfp2, dfp3, dfp4, dfp5, dfp6, dfp7], code, i)
        else:
            chg_p1,idx = GetFollowChangesByName(df, dfp1, code, i)
            chg_p2,idx = GetFollowChangesByName(dfp1, dfp2, code, idx)
            chg_p3,idx = GetFollowChangesByName(dfp2, dfp3, code, idx)
            chg_p4,idx = GetFollowChangesByName(dfp3, dfp4, code, idx)
            chg_p5,idx = GetFollowChangesByName(dfp4, dfp5, code, idx)
            chg_p6,idx = GetFollowChangesByName(dfp5, dfp6, code, idx)
            chg_p7,idx = GetFollowChangesByName(dfp6, dfp7, code, idx)
        pct_chg = round(chg_p1*100./(follows-chg_p1), 2)
        line = name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7
        list.append(line)
        # print line
    print "*** Result ***",
    print len(list), len(list[0]),
    list.sort(key=lambda data : data[2], reverse=True)
    print 'sorted.'
    rlist = list[:100]
    # Final 
    fcsv = open('watch_hk.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    for one in rlist:
        name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7 = one
        xq_code = code[code.find(':'):].replace('(','').replace(')','').replace(':','').upper()
        LiuTongYi = 0
        if CheckStar(name, code, chg_p1, pct_chg, chg_p2, chg_p3, LiuTongYi):
            stock_info_str = u'港股市值'+ GetStockInfo_fromFile(csv.reader(file('stockinfo_hk.csv','rb')),xq_code).decode('gbk')
            FollowsMultiple = round((chg_p1/GetFollowsMeanByCode(dirfilelist, code)), 2)
            print  '%-10s'%one[0].decode('gbk'), one[1], ',', one[2], ',[', float('%.1f' % FollowsMultiple),'x ]', str(one[3])+'%', ',', one[4:], stock_info_str, get_stock_lastday_status(one[1])
            if FollowsMultiple > 3:
                watch_line = 'hk', xq_code, FollowsMultiple, stock_info_str
                csvWriter.writerow(watch_line)
    fcsv.close()
    print filelist
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60      
    # GetFollowsChanges_InFileList(getFileList('./', 'stock_follows*.csv', False))
    GetFollowsChanges_InRecentFiles(getFileList('data/', '*.csv', False))
    # print get_stock_lastday_status('sh600036')