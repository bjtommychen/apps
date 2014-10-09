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

from pylab import *  
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] #指定默认字体
mpl.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题

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
    if startidx > 10:
        startidx -= 10
    # print code
    code = '('+code[:2]+':'+code[2:]+')'
    # print code
    for i in xrange(startidx, len(df1)):
        if df1['code'][i] != code:
            continue
        return df1['name'][i], df1['follows'][i]
    return '',0                    

    
        
def GetFollows_InFiles(rawlist, code):
    dirfilelist = []
    for one in rawlist:
        if 'stock_follows' in one:
            dirfilelist.append(one)
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

def GetFollows_ProcessList(followslist):
    list = []
    init_run = True
    for one in followslist:
        file, name, code, follows = one
        if init_run:
            init_run = False
            follows_prev = follows
            continue
        file = file.replace('./stock_follows-','')[:10]
        follows_chg = follows - follows_prev
        follows_chgpct = round((follows - follows_prev)*100./follows_prev, 2)
        follows_prev = follows
        line = file, follows_chg, follows_chgpct
        list.append(line)
    return list
    
def GetFollowsByCode_InFiles(filelist, code = 'SH600036'):
    print filelist
    code = code.upper()
    name, follows_list = GetFollows_InFiles(filelist, code)   
    # print follows_list
    follows_chg_list = GetFollows_ProcessList(follows_list)
    print name.decode('gbk')
    xdata = zip(*follows_chg_list)[0]
    df = DataFrame(follows_chg_list, index=xdata, columns=['DATE', 'CHG', 'CHG_PCT'])
    print df
    fig = plt.figure()
    ax_left = df.CHG.plot(kind='bar')
    ax_left.set_ylabel('Follows Change')
    ax_right = df.CHG_PCT.plot(secondary_y=True, style='R')
    ax_right.set_ylabel('Follows Change %')
    plt.title(name.decode('gbk')+code)
    plt.xlabel('Date')
    plt.show()
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Follows changes in csv file list.'
    print '#'*60
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store', dest='codename', default='SH600036', help='Specify the stock code name, Example:SH600036.')
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()    
    
    print args.codename
    GetFollowsByCode_InFiles(getFileList('./', '*.csv', False), args.codename)
