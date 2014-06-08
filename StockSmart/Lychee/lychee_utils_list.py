# -*- coding: utf-8 -*
import time
import sys
import os
from pandas import DataFrame, Series
import pandas as pd


print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')

filepath=unicode("watchlist.csv",'utf8')

df_watch = []

def list_show(dataf):
    print dataf

def list_load():
    global df_watch
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        print df
    else:
        header = ['market','code','price','ppk_limit']
        item = ['cn','sh600036',0.0,2.0]
        lists = []
        lists.append(item)
        item = ['us','jd',0.0,3.0]
        lists.append(item)

        df1 = DataFrame(data=lists, columns =header)
        print df1
        list_write(df1)
        df = pd.read_csv(filepath)
        print df
    df_watch = df.copy()
    return df_watch

def list_write(dataf):
    #global df
    global filepath
    dataf.to_csv(filepath, index=False)


if  __name__ == '__main__':
    print '#'*60
    print '##### Lychee utils list. ≤‚ ‘∞Ê' 
    print '#'*60
    print 'Config:'
    
    list_load()
    
    