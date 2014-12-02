# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import requests
import HTMLParser

from lychee_gtalk_io import *
from lychee_watchlist import *
from lychee_ParseWebPrice import *

# print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

stockmon_enable = True
stockmon_debug = False
stockmon_force = False
start_time = time.time()
update_interval_in_seconds = 30

cn_market_open = False
us_market_open = False
run_1st = True

wlist = []

def stockmon_enable_send(onoff):
    stockmon_enable = onoff        
    
def check_cn_market_open():
    global stockmon_enable
    checkopen = False
    if (datetime.datetime.now().weekday() > 4) and stockmon_enable:
        return False
    text = time.strftime("%H:%M", time.localtime())
    if text > '09:20' and text <= '11:30':
        checkopen = True
    elif text >= '13:00' and text <= '15:00':
        checkopen = True
    if stockmon_enable:
        print 'cn market status:', checkopen
    return checkopen

def check_us_market_open():
    checkopen = False
    if (datetime.datetime.now().weekday() > 4):
        return False
    text = time.strftime("%H:%M", time.localtime())
    if text >= '21:30' and text <= '23:59':
        checkopen = True
    elif text >= '00:00' and text <= '01:00':
        checkopen = True
    return checkopen    

def get_cn_rt_price(code):
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
        name = "%s" % data[0]
        name = string.replace(name,' ','')
        if (name):
            return (name, float(data[1]), float(data[2]), float(data[3]), 
                     float(data[4]), float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)    
    
   
#['market','code','name','price','ppk_limit']            
def stockmon_check_cn_stock(force):
    global cn_market_open
    global wlist
    strout = ''
    if not force and cn_market_open == check_cn_market_open() and cn_market_open == False:
        return ''
    if cn_market_open != check_cn_market_open():    #check if market status changed.
        cn_market_open = check_cn_market_open()
        force = True
    #get time
    timetext = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
    if not cn_market_open:
        timetext += 'Close'
    timetext += '\n'
    #check list
    wlist_stock = wlist
    need_printout = False
    print 'Check one by one, ',  len(wlist_stock)
    for i in range(0, len(wlist_stock)):
        if wlist_stock[i][0] != 'cn':
            continue
        # print 'checking', wlist_stock[i]
        name, openprice, lastclose, curr, todayhigh, todaylow = get_cn_rt_price(wlist_stock[i][1])
        # if stockmon_debug:
            # strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            strout += '%s: %s, %s, %s%%\n' %(name,curr, (curr-lastclose), day_chg_pct)
            wlist_stock[i][2] = '%s'% name.encode('gbk')
            need_printout = True
        elif wlist_stock[i][3] != curr and lastclose != 0:
            price_old = float(wlist_stock[i][3])
            if price_old == 0.0:
                price_old = 0.1
            diff_ppk = 0
            if price_old:
                diff_ppk = abs((curr - price_old)*1000/price_old)
                chg_ppk = ((curr - price_old)*1000/price_old)
            day_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            #print diff_ppk, day_chg_pct
            if (diff_ppk >= 10 or stockmon_debug) and day_chg_pct > 2:
                need_printout = True
                wlist_stock[i][2] = '%s'% name.encode('gbk')
                wlist_stock[i][3] = curr
                if chg_ppk > 0:
                    strout += '↑'
                if chg_ppk < 0:
                    strout += '↓'
                strout += '%s: %s, %s, %s%%, %sx, %s\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5])
    if need_printout:
        strout += timetext
    return strout

#['market','code','name','price','ppk_limit']            
def stockmon_check_us_stock(force):
    global us_market_open
    global wlist
    strout = ''
    if not force and us_market_open == check_us_market_open() and us_market_open == False:
        return ''
    if us_market_open != check_us_market_open():    #check if market status changed.
        us_market_open = check_us_market_open()
        force = True
    #get time
    timetext = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
    if not us_market_open:
        timetext += 'Close'
    timetext += '\n'
    #check list
    wlist_stock = wlist
    need_printout = False
    print 'Check us one by one, ',  len(wlist_stock)
    for i in range(0, len(wlist_stock)):
        if wlist_stock[i][0] != 'us':
            continue
        # print 'checking', wlist_stock[i]
        name, openprice, lastclose, curr, todayhigh, todaylow = get_us_rt_price(wlist_stock[i][1])
        # print name, openprice, lastclose, curr, todayhigh, todaylow
        if stockmon_debug:
            strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            strout += '%s: %s, %s, %s%%\n' %(name, curr, (curr-lastclose), day_chg_pct)
            wlist_stock[i][2] = '%s'% name
            need_printout = True
        elif wlist_stock[i][3] != curr and lastclose != 0:
            price_old = float(wlist_stock[i][3])
            if price_old == 0.0:
                price_old = 0.1
            diff_ppk = 0
            if price_old:
                diff_ppk = abs((curr - price_old)*1000/price_old)
                chg_ppk = ((curr - price_old)*1000/price_old)
            day_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            # print name, diff_ppk, day_chg_pct
            if (diff_ppk >= 10 or stockmon_debug) and day_chg_pct > 2:
                need_printout = True
                wlist_stock[i][2] = '%s'% name
                wlist_stock[i][3] = curr
                if chg_ppk > 0:
                    strout += '↑' #.encode('gbk')
                if chg_ppk < 0:
                    strout += '↓' #.encode('gbk')
                strout += '%s: %s, %s, %s%%, %sx, %s\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5])
    if need_printout:
        strout += timetext
    return strout

      
  
def stockmon_init(): 
    banner = '*** Stockmon Daemon. Longan Version. v1.0 ' 
    banner += '_us_cn_hk_RealTime_'
    banner += '\n'
    return banner    

def stockmon_exit():
    return 'stockmon_exit'    
    
def stockmon_process(force = False):
    global start_time
    global update_interval_in_seconds
    global stockmon_force
    global run_1st
    global wlist
    
    if run_1st:
        force = True
        run_1st = False
    if force:
        stockmon_force = True
    # update ?
    strout = ''
    curr_time = time.time()
    # if stockmon_debug:
        # print (curr_time - start_time)
    # update watch list
    list = watchlist_update() 
    if list != [] and len(list) > 0:
        # print list
        strout += 'WatchList updated ! new len:' + str(len(list)) + '\n'
        wlist = []
        count = 0
        for one in list:
            # if count > 5: 
                # break
            count += 1
            market, code, follows_multiple, market_value = one
            wlist.append([market, code, '', 0, float('%.1f' % float(follows_multiple)), market_value])
        # print 'new wlist:', wlist
        print 'new watchlist! len:', len(wlist)
    else:
        print '@',

    if not force and (curr_time - start_time) < update_interval_in_seconds:    #update intervals
        return strout
        
    start_time = curr_time
    # start to update
    #print 'stockmon_force', stockmon_force
    try:
        strout += stockmon_check_cn_stock(stockmon_force)
    except:
        strout += 'check cn stock except!'
    try:
        strout += stockmon_check_us_stock(stockmon_force)
    except:
        strout += 'check us stock except!'
    stockmon_force = False
    return strout
            
if  __name__ == '__main__':   
    force = False
    banner = stockmon_init()
    if True:
        Gtalk_init()
        Gtalk_run()
        Gtalk_send('Welcome tommy! Eye on Yours! ')
        Gtalk_send(banner)
    while True:
        msgstr = stockmon_process(force)
        if force:
            force = False
        if msgstr != '':
            print '*** Msg out *** \n'
            Gtalk_send(msgstr)
        time.sleep(5)
        print '.',
        
