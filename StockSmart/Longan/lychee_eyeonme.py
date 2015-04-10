# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import requests
import HTMLParser

from lychee_gtalk_io import *
from lychee_gtalk import *
from lychee_watchlist import *
from lychee_ParseWebPrice import *
from lychee_ui_center import *
from lychee_sys import *
from longan_savelogs import *

# print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

DebugMode = False

stockmon_enable = True
stockmon_debug = False
stockmon_force = False
start_time = time.time()
update_interval_in_seconds = 30

cn_market_open = False
hk_market_open = False
us_market_open = False
flag_heartbeat = False
stockmon_run1st = True

wlist = []

def stockmon_enable_send(onoff):
    stockmon_enable = onoff        

def check_heartbeat():
    # return True
    text = time.strftime("%H:%M", time.localtime())
    pos = text.find(':')
    if text[pos+1:] == '00':
        return True
    else:
        return False
    
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
    # if stockmon_enable:
        # print 'cn market status:', checkopen
    return checkopen

def check_hk_market_open():
    global stockmon_enable
    checkopen = False
    if (datetime.datetime.now().weekday() > 4) and stockmon_enable:
        return False
    text = time.strftime("%H:%M", time.localtime())
    if text > '09:20' and text <= '12:00':
        checkopen = True
    elif text >= '13:00' and text <= '16:00':
        checkopen = True
    # if stockmon_enable:
        # print 'cn market status:', checkopen
    return checkopen    
    
def check_us_market_open():
    checkopen = False
    if (datetime.datetime.now().weekday() > 5):
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
    print 'Check cn one by one, ',  len(wlist_stock)
    for i in range(0, len(wlist_stock)):
        if wlist_stock[i][0] != 'cn':
            continue
        #print 'checking', i, wlist_stock[i]
        oneprice = get_cn_rt_price(wlist_stock[i][1])
        if oneprice == [] or oneprice[0] == '':
            continue
        name, openprice, lastclose, curr, todayhigh, todaylow = oneprice
        #print oneprice
        # if stockmon_debug:
            # strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = round ((curr-lastclose)*100/lastclose, 1)
            open_chg_pct = round ((openprice-lastclose)*100/lastclose, 1)
            oneline = ''
            if open_chg_pct < 2:
                if day_chg_pct > 2:
                    oneline +='★'
                    if day_chg_pct < 5:
                        oneline +='★'        #Add one more Star
            if day_chg_pct > 0:
                oneline += '↑'
            elif day_chg_pct < 0:
                oneline += '↓'            
            oneline += '#%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5], open_chg_pct)
            strout += oneline
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
            open_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 1)
                open_chg_pct = round ((openprice-lastclose)*100/lastclose, 1)
            #print diff_ppk, day_chg_pct
            if wlist_stock[i][5] == 'hold':
                # if Hold Stock
                if diff_ppk >= 5 or stockmon_debug:
                    need_printout = True
                    wlist_stock[i][2] = '%s'% name.encode('gbk')
                    wlist_stock[i][3] = curr    #backup as last ref.
                    if day_chg_pct > 2:
                        strout +='★'
                        if day_chg_pct < 5:
                            strout +='★'        #Add one more Star
                    if chg_ppk > 0:
                        strout += '↑'
                    elif chg_ppk < 0:
                        strout += '↓'
                    strout += '%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)
            elif (diff_ppk >= 8 and day_chg_pct > 1) or stockmon_debug:
                # if Watch Stock
                need_printout = True
                wlist_stock[i][2] = '%s'% name.encode('gbk')
                wlist_stock[i][3] = curr    #backup as last ref.
                if open_chg_pct < 2:
                    if day_chg_pct > 2:
                        strout +='★'
                        if day_chg_pct < 5:
                            strout +='★'        #Add one more Star
                if chg_ppk > 0:
                    strout += '↑'
                elif chg_ppk < 0:
                    strout += '↓'                
                strout += '%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)

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
    timetext += '\n\n'
    #check list
    wlist_stock = wlist
    need_printout = False
    print 'Check us one by one, ',  len(wlist_stock)
    for i in range(0, len(wlist_stock)):
        if wlist_stock[i][0] != 'us':
            continue
        # print 'checking', wlist_stock[i]
        oneprice = get_us_rt_price(wlist_stock[i][1])
        if oneprice == []:
            continue
        name, openprice, lastclose, curr, todayhigh, todaylow = oneprice        
        
        # print name, openprice, lastclose, curr, todayhigh, todaylow
        if stockmon_debug:
            strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = round ((curr-lastclose)*100/lastclose, 1)
            open_chg_pct = round ((openprice-lastclose)*100/lastclose, 1)
            oneline = ''
            if open_chg_pct < 2:
                if day_chg_pct > 2:
                    oneline +='★'
                    if day_chg_pct < 5:
                        oneline +='★'        #Add one more Star
            if day_chg_pct > 0:
                oneline += '↑'
            elif day_chg_pct < 0:
                oneline += '↓'                 
            oneline += '#%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)
            strout += oneline
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
            open_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 1)
                open_chg_pct = round ((openprice-lastclose)*100/lastclose, 1)
            # print name, diff_ppk, day_chg_pct
            if wlist_stock[i][5] == 'hold':
                # if Hold Stock
                if diff_ppk >= 5 or stockmon_debug:
                    need_printout = True
                    wlist_stock[i][2] = '%s'% name
                    wlist_stock[i][3] = curr    #backup as last ref.
                    if day_chg_pct > 2:
                        strout +='★'
                        if day_chg_pct < 5:
                            strout +='★'        #Add one more Star
                    if chg_ppk > 0:
                        strout += '↑'
                    elif chg_ppk < 0:
                        strout += '↓'
                    strout += '%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)
            elif (diff_ppk >= 5 and day_chg_pct > 1) or stockmon_debug:
                # if Watch Stock
                need_printout = True
                wlist_stock[i][2] = '%s'% name
                wlist_stock[i][3] = curr    #backup as last ref.
                if open_chg_pct < 2:
                    if day_chg_pct > 2:
                        strout +='★'
                        if day_chg_pct < 5:
                            strout +='★'
                if chg_ppk > 0:
                    strout += '↑'
                elif chg_ppk < 0:
                    strout += '↓'
                strout += '%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)

    if need_printout:
        strout += timetext
    return strout

#['market','code','name','price','ppk_limit']            
def stockmon_check_hk_stock(force):
    global hk_market_open
    global wlist
    strout = ''
    if not force and hk_market_open == check_hk_market_open() and hk_market_open == False:
        return ''
    if hk_market_open != check_hk_market_open():    #check if market status changed.
        hk_market_open = check_hk_market_open()
        force = True
    #get time
    timetext = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
    if not hk_market_open:
        timetext += 'Close'
    timetext += '\n\n'
    #check list
    wlist_stock = wlist
    need_printout = False
    print 'Check hk one by one, ',  len(wlist_stock)
    for i in range(0, len(wlist_stock)):
        if wlist_stock[i][0] != 'hk':
            continue
        # print 'checking', wlist_stock[i]
        oneprice = get_hk_rt_price(wlist_stock[i][1])
        if oneprice == []:
            continue
        name, openprice, lastclose, curr, todayhigh, todaylow = oneprice
        # print name, openprice, lastclose, curr, todayhigh, todaylow
        if stockmon_debug:
            strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = round ((curr-lastclose)*100/lastclose, 1)
            open_chg_pct = round ((openprice-lastclose)*100/lastclose, 1)
            oneline = ''
            if open_chg_pct < 2:
                if day_chg_pct > 2:
                    oneline +='★'
                    if day_chg_pct < 5:
                        oneline +='★'        #Add one more Star
            if day_chg_pct > 0:
                oneline += '↑'
            elif day_chg_pct < 0:
                oneline += '↓'                  
            oneline += '#HK:%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)
            strout += oneline
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
            open_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 1)
                open_chg_pct = round ((openprice-lastclose)*100/lastclose, 1)
            # print name, diff_ppk, day_chg_pct
            if wlist_stock[i][5] == 'hold':
                # if Hold Stock
                if diff_ppk >= 5 or stockmon_debug:
                    need_printout = True
                    wlist_stock[i][2] = '%s'% name
                    wlist_stock[i][3] = curr    #backup as last ref.
                    if day_chg_pct > 2:
                        strout +='★'
                        if day_chg_pct < 5:
                            strout +='★'        #Add one more Star
                    if chg_ppk > 0:
                        strout += '↑'
                    elif chg_ppk < 0:
                        strout += '↓'
                    strout += 'HK%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)
            elif (diff_ppk >= 5 and day_chg_pct > 1) or stockmon_debug:
                # if Watch Stock
                need_printout = True
                wlist_stock[i][2] = '%s'% name
                wlist_stock[i][3] = curr    #backup as last ref.
                if open_chg_pct < 2:
                    if day_chg_pct > 2:
                        strout +='★'
                        if day_chg_pct < 5:
                            strout +='★'        #Add one more Star
                if chg_ppk > 0:
                    strout += '↑'
                elif chg_ppk < 0:
                    strout += '↓'      
                strout += 'HK%s: %s, %s, %s%%, %sx, %s,⋌%s%%\n' %(name, curr, (curr-lastclose), day_chg_pct, wlist_stock[i][4], wlist_stock[i][5],open_chg_pct)
    if need_printout:
        strout += timetext
    return strout      
  
def stockmon_init(): 
    banner = '*** Stockmon Daemon. \nLongan Version. v2.1 11:21 2015/3/20 ' 
    banner += '_us_cn_hk_RealTime_'
    banner += '\n'
    return banner    

def stockmon_exit():
    return 'stockmon_exit'    
    
def stockmon_process(force = False):
    global start_time
    global update_interval_in_seconds
    global stockmon_force
    global stockmon_run1st
    global wlist
    global flag_heartbeat
    
    if stockmon_run1st:
        force = True
        stockmon_run1st = False
    if force:
        stockmon_force = True
    # update ?
    strout = ''
    
    if flag_heartbeat != check_heartbeat():
        flag_heartbeat = check_heartbeat()
        if flag_heartbeat:
            return '!---$$$♋♥♓♥♐€€€---!'
        else:
            return ''
    
    curr_time = time.time()
    # if stockmon_debug:
        # print (curr_time - start_time)
    # update watch list
    list = watchlist_update() 
    if list != [] and len(list) > 0:
        # print list
        strout += 'WatchList updated ! len:' + str(len(wlist)) + ' -> ' + str(len(list)) + '\n'
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
        stockmon_force = True
    # else:
        # print '@',

    if not force and (curr_time - start_time) < update_interval_in_seconds:    #update intervals
        return strout
        
    start_time = curr_time
    # start to update
    #print 'stockmon_force', stockmon_force
    try:
        strout += stockmon_check_cn_stock(stockmon_force)
    except:
        strout += 'check CN except!\n'
    try:
        strout += stockmon_check_us_stock(stockmon_force)
    except:
        strout += 'check US except!\n'
    try:
        strout += stockmon_check_hk_stock(stockmon_force)
    except:
        strout += 'check HK except!\n'
    stockmon_force = False
    return strout
           
if  __name__ == '__main__':   
    # global stockmon_run1st
    # global DebugMode
    # Setting
    DebugMode = True
    stockmon_run1st = True
    # Init
    force = False
    SaveLogs_SetIntervalSeconds(600)
    if DebugMode:
        ui_use_gtalk_io = False
    else:
        ui_use_gtalk_io = True
    use_Gtalk = ui_use_gtalk_io

    # if use_Gtalk:
        # Gtalk_init()
        # Gtalk_run()
        # Gtalk_send('Welcome tommy! Eye on Yours! ')
        # Gtalk_send(banner)
    ui_init()
    try:
        print 'Enter mainloop ...'
        global ui_running
        while ui_running:
            # print 'ui_running', ui_running 
            cmds = ui_get_commands()
            if len(cmds)>0:
                # print '[INPUT]:', cmds
                output = ui_dispatch_commands(cmds)
                ui_put_str(output)
            
            if not DebugMode:
                msgstr = stockmon_process(force)
            else:
                msgstr = 'stockmon_process ' + str(force) + str(stockmon_run1st)
                stockmon_run1st = False
            if force:
                force = False
            if msgstr != '':
                if DebugMode:
                    ui_put_str('*** Msg out *** \n'+msgstr+ '*** Msg done ***\n')
                else:
                    ui_put_str(msgstr)
                    SaveLogs_SaveOneString(msgstr)
            if use_Gtalk:
                time.sleep(5)   
            # print '.',
    except Exception, e:
        print 'Mainloop except!' ,Exception,e
    finally:
        ui_exit()    
