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
savepng = False
save_fname = ''

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
        return float(mOpen), float(mClose), float(mVolume)
    else:
        return 0, 0, 0


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
        price_open, price_close, dayvolume = GetPriceByDate(pricehistory, filename)
        if price_open == 0: #invalid
            day_price = last_day_price
        else:
            day_price = price_close
            last_day_price = price_close
        line = filename, follows_chg, follows_chgpct, day_price, dayvolume
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
    global livemode
    
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
    if codemarket != 0:
        livemode = True
    return code
    
def GetXticksList(datelist):
    length = len(datelist)
    list = []
    listlabel = []
    idx = length - 1
    while idx >= 0:
        list.append(idx)
        listlabel.append(datelist[idx][5:])
        idx -= 30
    list.append(0)
    listlabel.append(datelist[0][5:])
    return list, listlabel
    
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
    
def GetFollowsByCode_InFiles(filelist, code = 'SH600036'):
    global codemarket
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
    df = DataFrame(follows_chg_list, index=xdata, columns=['DATE', 'CHG', 'CHG_PCT', 'PRICE', 'VOLUME'])
    # print df
    print df.tail(20)
    # print len(df)
    # print df.CHG.describe()
    CHG_mean = df.CHG.mean()
    print 'CHG_mean', CHG_mean
    # print [CHG_mean for x in range(10)]
    # return  #####
    # fig = plt.figure(figsize=(16,9))
    # fig, (ax0, ax1) = plt.subplots(nrows=2, figsize=(16,9))
    fig = plt.figure(figsize=(16,8.5))
    ax0 = fig.add_axes((0.1, 0.2, 0.8, 0.7))     #[left, bottom, width, height]
    
    # ax_left = ax0
    ax_left = df.CHG.plot(ax=ax0, kind='bar', alpha=0.5, align='center', linewidth=2)
    ax0.plot([CHG_mean for x in range(len(df))], 'g--', linewidth=2)
    ax_left.set_ylabel('f')
    ax_right = df.PRICE.plot(ax=ax0, secondary_y=True, color='red', marker='v', linewidth=2, alpha=0.7)
    ax_right.set_ylabel('price')
    
    if codemarket == 0:
        value_str = GetStockInfo_fromFile(csv.reader(file('stockinfo_cn.csv','rb')), code).decode('gbk')
        plt.title(name.decode('gbk')+code+' v'+value_str)
    else:
        plt.title(name.decode('gbk')+code)
    plt.xlabel('Date')
    # print type(plt.xlim())
    # print type(xdata), xdata, xdata[0]
    list, listlabel = GetXticksList(xdata)
    ax_left.set_xticks(list)
    ax_left.set_xticklabels([]) #(listlabel, fontsize='small')
    # plt.legend()
    # fig.autofmt_xdate()
    # ax1.set_title('volume')
    # plt.subplot(223, axisbg='r')
    ax1 = fig.add_axes((0.1, 0.05, 0.8, 0.15), sharex=ax0)
    
    ax_volume = df.VOLUME.plot(ax=ax1, kind='bar', color='green', linewidth=1, alpha=0.7)
    ax_volume.set_xticklabels([])
    ax_volume.set_xticklabels(listlabel, fontsize='small')
    ax_volume.set_xticks(list)
    ax_volume.set_ylabel('volume')
    ax1.plot([df.VOLUME.mean() for x in range(len(df))], 'g--', linewidth=2)
    
    # fig.subplots_adjust(bottom=0.8)
    # cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    # fig.colorbar(im, cax=cbar_ax)
    
    if not savepng:
        plt.show()
    else:
        fig.savefig(save_fname) #, dpi=140)
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store', dest='codename', default='SH600036', help='Specify the stock code name, Example:SH600036/AMCN/00410.')
    parser.add_argument('-path', action='store', dest='datapath', default='data/', help='Specify the path contains the follows-csv files')
    parser.add_argument('--debug', action='store_const', dest='debug', default=0, const=1, help='enable debug mode.') 
    parser.add_argument('--live', action='store_const', dest='live', default=False, const=True, help='Get stock day price from YahooWeb.') 
    parser.add_argument('--save', action='store', dest='save', default='notexist', help='Save to PNG format.') 
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()    
    
    if args.live:
        livemode = True
    if args.save != 'notexist':
        savepng = True
        save_fname = args.save
    GetFollowsByCode_InFiles(getFileList(args.datapath, '*.csv', False), args.codename)
