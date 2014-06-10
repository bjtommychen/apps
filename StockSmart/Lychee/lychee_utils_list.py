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
wlist_header = ['market','code','name','price','ppk_limit']
wlist_stock = []

def wlist_show(wlist):
    strout = ''
    for line in wlist:
        strout += str(line) + ' ' + line[2].decode('gbk') + '\n'
        #for one in line:
        #    strout += str(one)
        #strout += ' '
    return strout        

def wlist_getlist():
    global wlist_stock    
    return wlist_stock
    
def wlist_load():
    global wlist_stock
    #check if need init
    if not os.path.exists(filepath):
        print 'watch list init.'
        lists = []
        lists.append(['cn','sh600036','x',1.0,2.0])
        lists.append(['us','jd','x',0.1,5.0])
        wlist_write(lists)
    df = pd.read_csv(filepath)
    wlist_stock = []
    for i in range(len(df)):
        line = df.loc[i].tolist()
        if line[0] != 'us' and line[0] != 'cn':
            continue
        wlist_stock.append(line)
    return wlist_stock

def wlist_add(addlist):
    global wlist_stock
    if len(addlist) != 3:
        return
    items = [addlist[0], addlist[1], 'x', 1.0, addlist[2]]
    wlist_stock.append(items)
    wlist_write(wlist_stock)
    
def wlist_remove(code):    
    global wlist_stock
    #print wlist_stock
    for i in range(len(wlist_stock)):
        line = wlist_stock[i]
        if line[1] == code:
            wlist_stock.remove(line)
            wlist_write(wlist_stock)
            break
    #print wlist_stock

def wlist_save():
    global wlist_stock    
    wlist_write(wlist_stock)
    
def wlist_write(lists):
    global filepath
    global wlist_header
    dataf = DataFrame(data=lists, columns=wlist_header)
    dataf.to_csv(filepath, index=False)
    print 'list wrote:\n', dataf

if  __name__ == '__main__':
    print '#'*60
    print '##### Lychee utils list. ≤‚ ‘∞Ê' 
    print '#'*60
    print 'Config:'
    
    wlist = wlist_load()
    print wlist
    addlist = ['cn', 'sh61', 3.1]
    wlist_add(addlist)
    wlist_remove('sh333')
    wlist_remove('sh61')
    wlist_remove('sh61')
    wlist_remove('sh61')
    
    
    
    