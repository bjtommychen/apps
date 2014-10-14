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

def GetFollowChangesByName(df1, df2, name, startidx = 0):
    if startidx > 10:
        startidx -= 10
    for i in xrange(startidx, len(df1)):
        if df1['name'][i] != name:
            continue
        for j in xrange(startidx, len(df2)):
            if name == df2['name'][j]:
                follow_chg = df1['follows'][i] - df2['follows'][j]
                # print type(follow_chg)
                return follow_chg
    return 0                    

# 流通股本
def GetLiuTong_fromInfos(df1, name):
    name = name.replace('(','').replace(')','').replace(':','').lower()
    for i in xrange(0, len(df1)):
        if df1['A'][i] == name:
            num = (df1['K'][i])
            num = num.strip()
            if len(num) > 1:
                return (float)(df1['K'][i])
            else:
                return 0.0
    return 0.
    
def CheckStar(name, code, chg_p1, pct_chg, chg_p2, chg_p3, LiuTongYi):
    # print type(pct_chg), pct_chg, chg_p1, LiuTongYi
    if chg_p1 > 100 and pct_chg > 2.0 and LiuTongYi < 80:
        return True
    else:
        return False

def get_cn_rt_price(code):
    code = code.replace('(','').replace(')','').replace(':','').lower()
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
            return (name, float(data[1]), float(data[2]), float(data[3]), 
                     float(data[4]), float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)

def get_stock_lastday_status(code):
    name, openprice, lastclose, curr, todayhigh, todaylow = get_cn_rt_price(code)
    diff_pct = str(round(((curr - lastclose)*100/lastclose), 2))+'%'
    return lastclose, curr, diff_pct    
        
def GetFollowsChanges_InRecentFiles(rawlist):
    dirfilelist = []
    for one in rawlist:
        if 'stock_follows' in one:
            dirfilelist.append(one)
            
    filelist = dirfilelist[-6:]
    # print filelist
    dfp5 = pd.read_csv(filelist[0], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp4 = pd.read_csv(filelist[1], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp3 = pd.read_csv(filelist[2], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp2 = pd.read_csv(filelist[3], names = ['name', 'code', 'follows'], skiprows=[0])
    dfp1 = pd.read_csv(filelist[4], names = ['name', 'code', 'follows'], skiprows=[0])
    df   = pd.read_csv(filelist[5], names = ['name', 'code', 'follows'], skiprows=[0])
    df_stockinfo   = pd.read_csv('stock_info_converted.csv', names = ['A','B','C','D','E','F','G','H','I','J','K','L','M'], skiprows=[0])

    list = []
    for i in xrange(len(df)):
        # if i%100 == 0:
            # print '...',i,'...'
        name = df['name'][i]
        code = df['code'][i]
        # print name, code, GetLiuTong_fromInfos(df_stockinfo,code)
        follows = df['follows'][i]
        chg_p1 = GetFollowChangesByName(df, dfp1, name, i)
        chg_p2 = GetFollowChangesByName(dfp1, dfp2, name, i)
        chg_p3 = GetFollowChangesByName(dfp2, dfp3, name, i)
        chg_p4 = GetFollowChangesByName(dfp3, dfp4, name, i)
        chg_p5 = GetFollowChangesByName(dfp4, dfp5, name, i)
        pct_chg = round(chg_p1*100./(follows-chg_p1), 2)
        line = name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5
        list.append(line)
    print "*** Result ***",
    print len(list), len(list[0]),
    list.sort(key=lambda data : data[2], reverse=True)
    print 'sorted.'
    rlist = list[:100]
    for one in rlist:
        name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5 = one
        LiuTongYi= GetLiuTong_fromInfos(df_stockinfo, one[1])/10000
        if CheckStar(name, code, chg_p1, pct_chg, chg_p2, chg_p3, LiuTongYi):
            print  '%-10s'%one[0].decode('gbk'), one[1], one[2], str(one[3])+'%', one[4:], str(LiuTongYi)+u'亿', get_stock_lastday_status(one[1])
    print filelist
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60      
    # GetFollowsChanges_InFileList(getFileList('./', 'stock_follows*.csv', False))
    GetFollowsChanges_InRecentFiles(getFileList('./', '*.csv', False))
    # print get_stock_lastday_status('sh600036')