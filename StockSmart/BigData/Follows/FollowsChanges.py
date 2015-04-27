import time
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

reload(sys) 
sys.setdefaultencoding('utf')

DebugMode = False

def save2csv(fname, list):
    fcsv = open(fname, 'wb')
    csvWriter = csv.writer(fcsv)
    csvWriter.writerows(list)
    fcsv.close()
        
def loadfromecsv(fname):
    list = []
    reader = csv.reader(file(fname,'rb'))
    for line in reader:        
        list.append(line)
    return list

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            # print fullname
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
    # if startidx > 10:
        # startidx -= 10
    # print startidx
    range = 50
    for i in xrange(startidx, len(df1)):
        if df1['name'][i] != name:
            continue
        # try fast mode first.
        if startidx > range:
            startidx -= range
        for j in xrange(startidx, min(startidx+range*2, len(df2))):
            if name == df2['name'][j]:
                follow_chg = df1['follows'][i] - df2['follows'][j]
                # print type(follow_chg)
                return follow_chg, j
        # use normal way
        for j in xrange(0, len(df2)):
            if name == df2['name'][j]:
                follow_chg = df1['follows'][i] - df2['follows'][j]
                return follow_chg, j
        break        
                
    return 0, 0

def GetStockInfo_fromFile(reader, check_code):
    # name = name.replace('(','').replace(')','').replace(':','').lower()
    check_code = check_code[2:]
    for one in reader:
        # print one, code
        code, name, info = one
        # print code,check_code
        if code == check_code:
            return info
    return 'N/A'

list_stockinfo = []
def GetStockInfo_cn(check_code):
    global list_stockinfo
    if list_stockinfo == []:
        list_stockinfo = loadfromecsv('stockinfo_cn.csv')
        print 'list_stockinfo', len(list_stockinfo)
    check_code = check_code[2:]
    first_or_default = next((x for x in list_stockinfo if x[0]==check_code), None)
    if first_or_default == None:
        return 'N/A'
    else:
        return first_or_default[2]
    
def CheckStar(name, code, chg_p1, pct_chg, chg_p2, chg_p3, LiuTongYi):
    # print type(pct_chg), pct_chg, chg_p1, LiuTongYi
    if chg_p1 > 200 and pct_chg > 2.0: # and LiuTongYi < 180:
        return True
    else:
        return False

def get_cn_rt_price(code='SH600036'):
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
    if lastclose == 0:
        name, openprice, lastclose, curr, todayhigh, todaylow = get_cn_rt_price(code)
    diff_pct = open_pct = '%Error'
    if lastclose != 0:
        diff_pct = str(round(((curr - lastclose)*100/lastclose), 1))+'%'
        open_pct = str(round(((openprice - lastclose)*100/lastclose), 1))+'%'
    return lastclose, curr, diff_pct, open_pct    
        
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
        
def PrintListForWeb(list_web):
    i = 0
    for one in list_web:
        i += 1
        if i%10 == 0:
            print one
        else:
            print one+',',
    print ''    
        
def GetFollowsChanges_InRecentFiles(rawlist):
    dirfilelist = []
    for one in rawlist:
        if 'stock_follows' in one:
            dirfilelist.append(one)
            
    # print GetFollowsMeanByCode(dirfilelist)
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
    # df_stockinfo   = pd.read_csv('stockinfo_cn.csv', names = ['code','name','info1'], skiprows=[0])

    list = []
    for i in xrange(len(df)):
        if i%100 == 0:
            print '.',
        name = df['name'][i]
        code = df['code'][i]
        xq_code = code.replace('(','').replace(')','').replace(':','').lower()
        # print name, code, GetStockInfo_fromFile(csv.reader(file('stockinfo_cn.csv','rb')) , xq_code)
        follows = df['follows'][i]
        chg_p1,idx = GetFollowChangesByName(df, dfp1, name, i)
        chg_p2,idx = GetFollowChangesByName(dfp1, dfp2, name, idx)
        chg_p3,idx = GetFollowChangesByName(dfp2, dfp3, name, idx)
        chg_p4,idx = GetFollowChangesByName(dfp3, dfp4, name, idx)
        chg_p5,idx = GetFollowChangesByName(dfp4, dfp5, name, idx)
        chg_p6,idx = GetFollowChangesByName(dfp5, dfp6, name, idx)
        chg_p7,idx = GetFollowChangesByName(dfp6, dfp7, name, idx)
        pct_chg = round(chg_p1*100./(follows-chg_p1), 1)
        line = name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7
        list.append(line)
        # print line
    print "*** Result ***",
    print len(list), len(list[0]),
    # print list
    list.sort(key=lambda data : data[2], reverse=True)
    print 'sorted.'
    rlist = list[:100]
    ############ watch ############
    if True:
        list_web = []
        fcsv = open('watch_cn.csv', 'wb')
        csvWriter = csv.writer(fcsv)
        for one in rlist:
            # break
            name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7 = one
            xq_code = code.replace('(','').replace(')','').replace(':','').lower()
            LiuTongYi = 0
            if CheckStar(name, code, chg_p1, pct_chg, chg_p2, chg_p3, LiuTongYi):
                value_str = GetStockInfo_fromFile(csv.reader(file('stockinfo_cn.csv','rb')), xq_code).decode('gbk')
                stock_info_str = u'总市值'+ value_str
                FollowsMultiple = round((chg_p1/GetFollowsMeanByCode(dirfilelist, code)), 1)
                if FollowsMultiple >= 3:
                    print  '%-10s'%one[0].decode('gbk'), one[1], ', ', one[2], ', [', float('%.1f' % FollowsMultiple),'x ]', str(one[3])+'%', ', ', one[4:], stock_info_str, get_stock_lastday_status(one[1])
                if FollowsMultiple >= 4 and chg_p1 > 200:
                    list_web.append(xq_code)
                    watch_line = 'cn', xq_code, FollowsMultiple, value_str
                    csvWriter.writerow(watch_line)
        PrintListForWeb(list_web)
        fcsv.close()
        
    ############# CatchSpurt_cn ##########    
    if True:
        rlist = list[:500]
        list_web = []
        # Final 
        fcsv = open('catchspurt_cn.csv', 'wb')
        csvWriter = csv.writer(fcsv)
        i = 0
        for one in rlist:
            i += 1
            # break
            name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7 = one
            xq_code = code.replace('(','').replace(')','').replace(':','').lower()
            LiuTongYi = 0
            if chg_p1 > 50 and chg_p1 < 200 and pct_chg > 5:
                # value_str = GetStockInfo_fromFile(csv.reader(file('stockinfo_cn.csv','rb')), xq_code).decode('gbk')
                value_str = GetStockInfo_cn(xq_code).decode('gbk')
                if '亿' not in value_str:
                    continue
                LiuTongYi = int(value_str.replace('亿',''))
                # print LiuTongYi
                stock_info_str = u'总市值'+ value_str
                FollowsMultiple = round((chg_p1/GetFollowsMeanByCode(dirfilelist, code)), 1)
                if FollowsMultiple >= 10 and chg_p1 > 50 and LiuTongYi < 120:
                    watch_line = 'cn', xq_code, FollowsMultiple, value_str
                    csvWriter.writerow(watch_line)
                    list_web.append(xq_code)
                    print '****** No.', i, '%-10s'%one[0].decode('gbk'), watch_line, stock_info_str, 'chg', chg_p1, str(pct_chg)+'%', str(FollowsMultiple)+'x'
        fcsv.close()
        PrintListForWeb(list_web)
    
    print filelist
    #Update hold_cn.csv
    ############ hold ############
    if True:
        list_web = []
        reader = csv.reader(file('hold_cn.csv','rb'))
        list_out = []
        for row in reader:
            # print row
            if len(row) != 4:
                continue
            market_str, hold_code, FollowsMultiple, comments = row
            for one in list:
                name, code, chg_p1, pct_chg, chg_p2, chg_p3, chg_p4, chg_p5, chg_p6, chg_p7 = one
                xq_code = code.replace('(','').replace(')','').replace(':','').lower()
                if hold_code == xq_code:
                    FollowsMultiple = round((chg_p1/GetFollowsMeanByCode(dirfilelist, code)), 1)
                    value_str = GetStockInfo_fromFile(csv.reader(file('stockinfo_cn.csv','rb')), xq_code).decode('gbk')
                    stock_info_str = u'总市值'+ value_str
                    print code, name.decode('gbk'), str(FollowsMultiple)+'x', one[2:], stock_info_str, get_stock_lastday_status(one[1])
                    break
            line = market_str, hold_code, FollowsMultiple, comments
            print line
            list_web.append(hold_code)
            list_out.append(line)
        
        PrintListForWeb(list_web)
        fcsv = open('hold_cn.csv', 'wb')
        csvWriter = csv.writer(fcsv)
        for line in list_out:                    
            csvWriter.writerow(line)
        fcsv.close()    
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60      
    # GetFollowsChanges_InFileList(getFileList('./', 'stock_follows*.csv', False))
    GetFollowsChanges_InRecentFiles(getFileList('data/', '*.csv', False))
    # print get_stock_lastday_status('sh600036')