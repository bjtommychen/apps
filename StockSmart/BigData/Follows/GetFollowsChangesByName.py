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
import matplotlib.pyplot as plt
import argparse

reload(sys) 
sys.setdefaultencoding('utf')

livemode = False

from pylab import *  
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] #指定默认字体
mpl.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题

codemarket = 0  # 0: cn, 1: hk, 2: us

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

def GetFollowsByCode(df1, code, startidx = 0):
    global codemarket 
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
        code2 = '('+code[:2]+':'+code[2:]+')'
        # print code2
        for i in xrange(startidx, len(df1)):
            if df1['code'][i] != code2:
                continue
            return df1['name'][i], df1['follows'][i]
    return '',0                    

    
        
def GetFollows_InFiles(rawlist, code):
    global codemarket 
    dirfilelist = []
    for one in rawlist:
        # print one
        if 'stock_follows' in one and codemarket == 0:
            dirfilelist.append(one)
        if 'hk' in one and codemarket == 1:
            dirfilelist.append(one)
        if 'nasdaq' in one and codemarket == 2:
            dirfilelist.append(one)
    # print dirfilelist
    init_run = True
    list = []      
    name_good = 'name_notready'
    for one in dirfilelist:
        # print one,
        df_curr = pd.read_csv(one, names = ['name', 'code', 'follows'], skiprows=[0])
        name, follows = GetFollowsByCode(df_curr, code)
        # print name, follows, one
        if follows > 0:
            name_good = name
            line = one, name, code, follows
            list.append(line)
        # print follows
    return name_good, list

def GetPriceByDate(list, date):
    first_or_default = next((x for x in list if x[0]==date), None)
    if first_or_default != None and len(first_or_default) == 7:
        mDate, mOpen, mHigh, mLow, mClose, mVolume, mAdj = first_or_default
        return float(mOpen), float(mClose)
    else:
        return 0, 0


    for row in list:
        if (len(row) != 7):
            print len(row), 'must be 7!!!'
            continue
        mDate, mOpen, mHigh, mLow, mClose, mVolume, mAdj = row
        if date == mDate:
            return float(mOpen), float(mClose) 
    return 0, 0
    
def GetFollows_ProcessList(followslist, filename_pricehistory):
    global nameprefix  
    list = []
    init_run = True
    last_day_price = 0
    day_price = 0
    print 'Open', filename_pricehistory
    reader = csv.reader(file(filename_pricehistory,'rb'))
    pricehistory = []
    for row in reader:
        pricehistory.append(row)
    for one in followslist:
        filename, name, code, follows = one
        if init_run:
            init_run = False
            follows_prev = follows
            continue
        filename = filename.replace(nameprefix,'')[:10]
        follows_chg = follows - follows_prev
        follows_chgpct = round((follows - follows_prev)*100./follows_prev, 2)
        follows_prev = follows
        price_open, price_close = GetPriceByDate(pricehistory, filename)
        if price_open == 0: #invalid
            day_price = last_day_price
        else:
            day_price = price_open
            last_day_price = price_close
        line = filename, follows_chg, follows_chgpct, day_price
        list.append(line)
    return list
    
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
    
def get_stock_history_csv_live(code, name):
    url = 'http://ichart.finance.yahoo.com/table.csv?s=' + yahoo_name_convert(code)+'&a=8&b=1&c=2014'
    local = 'stock_history_price.csv'
    if False: #os.path.exists(local):
        print local, 'exist! skip!'
    else:  
        print 'Get stock_history_csv for', name, ', url:', url
        socket.setdefaulttimeout(4)
        try: 
            urllib.urlretrieve(url, local, 0)
        except:
            exit(1)
        print 'Got csv file, size:', os.path.getsize(local), 'bytes!'
    return local

def get_stock_history_csv(code, name):
    if livemode:
        return get_stock_history_csv_live(code, name)
    else:
        filename = 'output_qda/'+ code + '_qda.csv'
        if os.path.exists(filename):
            return filename
        else:
            print filename, 'NOT exist.'
            return ''
        
        
def CodeName_AutoCompleted(code):
    if len(code) == 6:      #SH,SZ
        if code.isdigit():
            if code[0] == '6':
                code = 'SH:' + code
            elif code[0] == '3' or code[0] == '0':
                code = 'SZ:' + code
    elif len(code) == 5:    #HK
        if code.isdigit():
            code = 'HK:' + code
    return code
    
def CodeName_process(code):
    global codemarket
    global nameprefix    
    code = CodeName_AutoCompleted(code)
    code = code.upper()
    code = code.replace(':','')
    if code.find('SH') != -1:
        codemarket = 0
        nameprefix = 'data/stock_follows-'
    elif code.find('SZ') != -1:
        codemarket = 0
        nameprefix = 'data/stock_follows-'
    elif code.find('HK') != -1:
        codemarket = 1
        nameprefix = 'data/hk-'
    else:
        codemarket = 2
        nameprefix = 'data/nasdaq-'
    return code
    
def GetFollowsByCode_InFiles(filelist, code = 'SH600036'):
    # print filelist
    code = CodeName_process(code)
    print 'code:', code
    name, follows_list = GetFollows_InFiles(filelist, code)   
    print name.decode('gbk')
    csvfilename = get_stock_history_csv(code, name.decode('gbk'))
    print csvfilename
    if csvfilename == '':
        print 'csv file not found. exit.'
        return
    # print 'follows_list:', follows_list
    follows_chg_list = GetFollows_ProcessList(follows_list, csvfilename) 
    xdata = zip(*follows_chg_list)[0]   #get DataFrame from List
    df = DataFrame(follows_chg_list, index=xdata, columns=['DATE', 'CHG', 'CHG_PCT', 'PRICE'])
    # print df
    print df.tail(20)
    # print len(df)
    # print df.CHG.describe()
    CHG_mean = df.CHG.mean()
    print 'CHG_mean', CHG_mean
    # print [CHG_mean for x in range(10)]
    # return  #####
    fig = plt.figure()
    ax_left = df.CHG.plot(kind='bar', alpha=0.5, align='center', linewidth=2)
    plt.plot([CHG_mean for x in range(len(df))], 'g--')
    ax_left.set_ylabel('Follows Change')
    ax_right = df.PRICE.plot(secondary_y=True, color='red', marker='v', linewidth=2, alpha=0.7)
    ax_right.set_ylabel('PRICE')
    plt.title(name.decode('gbk')+code)
    plt.xlabel('Date')
    # plt.legend()
    fig.autofmt_xdate()
    plt.show()
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store', dest='codename', default='SH600036', help='Specify the stock code name, Example:SH600036.')
    parser.add_argument('-path', action='store', dest='datapath', default='data/', help='Specify the path contains the follows-csv files')
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--live', action='store_const', dest='live',default=False,const=True,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()    
    
    if args.live:
        livemode = True
    GetFollowsByCode_InFiles(getFileList(args.datapath, '*.csv', False), args.codename)
