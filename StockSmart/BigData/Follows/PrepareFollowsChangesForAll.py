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

'''
按照股票列表stocklist_cn.csv
从data目录读入每天获取的follows信息. 
按照独立股票, 单独统计, 写入文件到follows_history里. 
利于以后的交易模拟, 和加速.
'''

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
    for one in dirfilelist:
        # print one,
        df_curr = pd.read_csv(one, names = ['name', 'code', 'follows'], skiprows=[0])
        name, follows = GetFollowsByCode(df_curr, code)
        if follows > 0:
            line = one, name, code, follows
            list.append(line)
        # print follows
    return name, list
    
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
    
def GetFollowsByCode_StoreInFiles(filelist, code = 'SH600036'):
    # print filelist
    code = CodeName_process(code)
    print 'code:', code
    name, followslist = GetFollows_InFiles(filelist, code)   
    print name.decode('gbk')
    init_run = True
    list = []
    for one in followslist:
        filename, name, code, follows = one
        if init_run:
            init_run = False
            follows_prev = follows
            continue
        filename = filename.replace(nameprefix,'')[:10]
        follows_chg = follows - follows_prev
        follows_prev = follows        
        line = name, filename, follows, follows_chg
        # print line
        list.append(line)
    return list
    
def GetFollowsCSVforAll(filelist):
    reader = csv.reader(file('stocklist_cn.csv','rb'))
    error_count = 0    
    for row in reader:
        code, name = row
        if code[0] == '6':
            codestr = 'SH' + code
        else:
            codestr = 'SZ' + code        
        # print codestr
        list = GetFollowsByCode_StoreInFiles(filelist, codestr)
        print 'len:', len(list)
        if len(list) > 0:
            fcsv = open('follows_history/'+codestr+'.csv', 'wb')
            csvWriter = csv.writer(fcsv)
            # for one in titles:
            csvWriter.writerows(list)
            fcsv.close()
        # return
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('-t', action='store', dest='codename', default='SH600036', help='Specify the stock code name, Example:SH600036.')
    parser.add_argument('-path', action='store', dest='datapath', default='data/', help='Specify the path contains the follows-csv files')
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()    
    
    # print args.codename
    filelist_csv = getFileList(args.datapath, '*.csv', False)
    GetFollowsCSVforAll(filelist_csv)
    print 'Done!'
