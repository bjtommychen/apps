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
watchlist_header = ['market','code','name','price','ppk_limit']
df_watch = []

def list_show(df_watch):
    print df_watch

def list_load():
    global df_watch
    #check if need init
    if not os.path.exists(filepath):
        print 'watch list init.'
        lists = []
        lists.append(['cn','sh600036','',0.0,2.0])
        lists.append(['us','jd','',0.0,3.0])
        list_write(lists)
    df = pd.read_csv(filepath)
    df_watch = []
    for i in range(len(df)):
        line = df.loc[i].tolist()
        df_watch.append(line)
    return df_watch

def list_add(addlist):
    global df_watch
    if len(addlist) != 3:
        return
    items = [addlist[0], addlist[1], 'x', 0, addlist[2]]
    df_watch.append(items)
    list_write(df_watch)
    
def list_remove(code):    
    global df_watch
    #print df_watch
    for i in range(len(df_watch)):
        line = df_watch[i]
        if line[1] == code:
            df_watch.remove(line)
            list_write(df_watch)
            break
    #print df_watch
    
def list_write(lists):
    global filepath
    global watchlist_header
    dataf = DataFrame(data=lists, columns =watchlist_header)
    dataf.to_csv(filepath, index=False)
    print 'list wrote:\n', dataf

if  __name__ == '__main__':
    print '#'*60
    print '##### Lychee utils list. ≤‚ ‘∞Ê' 
    print '#'*60
    print 'Config:'
    
    wlist = list_load()
    print wlist
    addlist = ['cn', 'sh61', 3.1]
    list_add(addlist)
    list_remove('sh333')
    list_remove('sh61')
    list_remove('sh61')
    list_remove('sh61')
    
    
    
    