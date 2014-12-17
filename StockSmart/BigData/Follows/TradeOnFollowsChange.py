import time
import sys
import os
import math
import csv
import stat,fnmatch
import struct
from pandas import DataFrame, Series
import pandas as pd
import string
import datetime, dateutil

reload(sys) 
sys.setdefaultencoding('utf')

def Hlist_FindHigh(list):
    dayhigh = 0.0
    line = None
    for one in list:
        mDate, mOpen, mHigh, mLow, mClose = one
        if mHigh > dayhigh:
            dayhigh = mHigh
            line = one
    return line
    
def AnalyseHistoryPrice(code, name, FollowsMultiple, date):
    d_start = dateutil.parser.parse(date)
    filename = 'history_data/'+code+'.csv'
    if not os.path.exists(filename):
        return None  
    reader = csv.reader(file(filename,'rb'))
    hlist = []
    price_start = 0.1
    for row in reader:
        if (len(row) != 7):
            print len(row), 'must be 7!!!'
            continue
        mDate, mOpen, mHigh, mLow, mClose, mVolume, mAdj = row
        if mDate == 'Date' or (float(mHigh) == float(mLow)):
            continue
        line = mDate, float(mOpen), float(mHigh), float(mLow), float(mClose)
        hlist.append(line)
        # print line
        if mDate == date:
            price_start = float(mOpen)
            break
    if len(hlist) < 1 or price_start < 1:
        return None
    line_DayHigh = Hlist_FindHigh(hlist)
    print code, name, line_DayHigh
    mDate, mOpen, mHigh, mLow, mClose = line_DayHigh
    DeltaDay = dateutil.parser.parse(mDate) - d_start
    ProfitPct = round((mHigh - price_start)*100.0/price_start, 1)
    print '-'*30, 'DeltaDay:',DeltaDay.days, ', Profit:', ProfitPct, '%'
    if DeltaDay.days > 0 and DeltaDay.days < 30:
        return code,name, FollowsMultiple, date, price_start, mDate, mHigh, DeltaDay.days, ProfitPct
    else:
        return None
    
    
        
def FollowsInfoByCode(code):
    filename = 'follows_history/'+code+'.csv'
    if not os.path.exists(filename):
        # print filename, 'not exit'
        return None
    reader = csv.reader(file(filename,'rb'))
    follows_chg_list = []
    rt_line = []
    for row in reader:
        name, date, follows, follows_chg = row
        follows_chg = int(follows_chg)
        follows_chg_list.append((follows_chg))
        if date > '2014-10-08' and date < '2014-12-01':
            df = Series(follows_chg_list)
            FollowsMultiple = round((follows_chg)/df.mean(), 1)
            if FollowsMultiple > 4 and FollowsMultiple < 50:
                d = dateutil.parser.parse(date)
                if d.weekday() < 5:
                    print code, name, d, ',', follows, follows_chg, round(df.mean(),1), str(FollowsMultiple)+'x'
                    line = AnalyseHistoryPrice(code, name, FollowsMultiple, date)
                    if line != None:
                        rt_line.append(line)
    return rt_line
                        
def AnalyseFollowsInfoAll():
    reader = csv.reader(file('stocklist_cn.csv','rb')) 
    fcsv = open('AnalyseFollowsInfoAll.csv', 'wb')
    csvWriter = csv.writer(fcsv)    
    print 'Got list from csv'
    for one in reader:
        code, name = one
        if code[0] == '6':
            codestr = 'sh' + code
        else:
            codestr = 'sz' + code
        # print codestr
        line = FollowsInfoByCode(codestr)
        if line != None and len(line)>0:
            for one in line:
                csvWriter.writerow(one)
    fcsv.close()                    
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Trade! Trade! Trade!'
    print '#'*60
    FollowsInfoByCode('SH600036')
    AnalyseFollowsInfoAll()
    # FollowsInfoByCode('sh600036')
