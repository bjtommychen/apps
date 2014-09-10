# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from lychee_gtalk_io import *
from lychee_utils_list import *
from selenium import webdriver
from lychee_webdrv import *
import requests

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')

stockmon_enable = True
stockmon_debug = False
stockmon_force = False
start_time = time.time()
update_interval_in_seconds = 60

cn_market_open = False
us_market_open = False
run_1st = True

wd = None
us_list = ['jd', 'amcn', 'dang']

def stockmon_process_cmds(cmds):
    print 'stockmon_process_cmds', cmds
    strout = ''
    if (len(cmds) == 0):
        strout += 'stockmon help - for more.'
    else:    
        if cmds[0] == 'help' or cmds[0] == '?':
            strout += 'stockmon help:\n'+ \
                '\thelp - print help \n'+\
                '\ton - stockmon on \n' +\
                '\toff - stockmon off \n' +\
                '\tdebug - stockmon debug mode \n' +\
                '\tlistall - show watch list \n' +\
                '\tadd [country] [code] [ppk] - add to list: cn sh60036 2 \n' +\
                '\tremove [code] - remove item from list\n' +\
                '\tsave - save list to disk\n' +\
                '\tforceshow - force to show all list\n' +\
                ''
        elif cmds[0] == 'on':
            stockmon_enable_send(True)
            strout += 'stockmon set on.'
        elif cmds[0] == 'off':
            stockmon_debug = False
            stockmon_enable_send(False)
            strout += 'stockmon set off.'
        elif cmds[0] == 'debug':
            stockmon_debug = True
            strout += 'stockmon set debug on.'
        elif cmds[0] == 'listall':
            wlist = wlist_getlist()
            strout += 'watch list: \n' + wlist_show(wlist)
        elif cmds[0] == 'add':
            wlist = [cmds[1], cmds[2], cmds[3]]
            wlist_add(wlist)
            strout += 'watch list add: \n' + str(wlist)
        elif cmds[0] == 'remove':
            wlist = cmds[1]
            wlist_remove(wlist)
            strout += 'watch list remove: \n' + str(wlist)
        elif cmds[0] == 'save':
            wlist_save()
            strout += 'watch list save to disk\n'
        elif cmds[0] == 'forceshow':
            global stockmon_force
            stockmon_force = True
            strout += stockmon_process(stockmon_force)
        else:
            strout += 'invalid command'
    #print strout        
    return strout

def stockmon_enable_send(onoff):
    stockmon_enable = onoff        
    
def check_cn_market_open():
    checkopen = False
    if (datetime.datetime.now().weekday() > 4):
        return False
    text = time.strftime("%H:%M", time.localtime())
    if text > '09:20' and text <= '11:30':
        checkopen = True
    elif text >= '13:00' and text <= '15:00':
        checkopen = True
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
#CN    
def get_cn_rt_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
    #print url
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

#US, name, openprice, lastclose, curr, todayhigh, todaylow
us_url_swap = 1
def get_us_rt_price_yahoo(code):    # DELAY 15 MINUTES
    global us_url_swap
    if us_url_swap == 1:
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=nopl1hg' % code
    else:
        url = 'http://quote.yahoo.com/d/quotes.csv?s=%s&f=nopl1hg' % code
    us_url_swap = (us_url_swap+1)%2
    #print url
    try:
        sock = urllib.urlopen(url)
        strs = sock.readline()
        sock.close()
        if 'strict' in strs:
            return ('', 0, 0, 0, 0, 0) 
    except Exception, e:
        return ('', 0, 0, 0, 0, 0) 
    else:
        strs = string.replace(strs,'\r\n','')
        data = strs.split('"')[2].split(',')
        name = strs.split('"')[1]
        if (name):
            return (name, float(data[1]), float(data[2]), float(data[3]), 
                     float(data[4]), float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)                

# SOHU
def get_us_rt_price_sohu_done():
    global wd
    #if wd != None:
    #    wd.close()
    #wd =None
    return
    
def get_us_rt_price_sohu(code):
    global wd
    code = code.upper()
    url = 'http://quotes.money.163.com/usstock/%s.html#2u01' % code
    #print url, '---------------------------------------------'
    if wd == None:
        prof=webdriver.FirefoxProfile()
        prof.set_preference("permissions.default.stylesheet", 2)
        prof.set_preference("permissions.default.image", 2)
        prof.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)        
        wd = webdriver.Firefox(prof)
        
    #wd = webdrv_get()
    wd.get(url)
    print len(wd.page_source)
    if len(wd.page_source) < 1000:
        print wd.page_source.encode('utf8')
        return ('', 0, 0, 0, 0, 0) 
    a = wd.find_elements_by_class_name('stock_info')
    if a == []:
        print 'error a', a
        return ('', 0, 0, 0, 0, 0) 
    c = a[0].find_element_by_class_name('price').text
    d = c.split()
    if len(d) != 3:
        print 'error len d', len(d), d
        return ('', 0, 0, 0, 0, 0) 
    #print d
    name = code
    curr = float(d[1])
    lastclose = float(d[1]) - float(d[2])
    #print curr, lastclose
    a = wd.find_elements_by_class_name('stock_detail_info')
    #wd.close()
    #wd = None
    #print len(a)
    d = a[0].text.split()
    #print d, d[2:]
    #for one in a:
    #    print one.text
    #print 'Open price ', d[0], len(d[0]), d[0][2:], d[0][2:].isdigit()
    if len(d[0]) > 2 and d[0][2].isdigit():
        #for i in range(0, len(d[0])):
        #    print d[0][i].isdigit()
        openprice = float(d[0][2:])
        todayhigh = todaylow = 0
        print 'SOHU DONE!',(name, openprice, lastclose, curr, todayhigh, todaylow)
        return (name, openprice, lastclose, curr, todayhigh, todaylow)
    else:
        print 'lenght less than 2'
    print 'error! ', d[0], len(d[0]), d[0][2:], d[0][2:].isdigit()
    return ('', 0, 0, 0, 0, 0)             
   
#GOOGLE    
def get_us_rt_price_GoogleWeb(code):
    global wd
    code = code.upper()
    url = 'http://www.google.com/finance?q=%s' % code
    print url, '---------------------------------------------'
    if wd == None:
        wd = webdriver.Firefox()
        print 'Create webd'
    wd.get(url)
    print len(wd.page_source)
    if len(wd.page_source) < 500:
        print wd.page_source.encode('utf8')
        return ('', 0, 0, 0, 0, 0) 
    a = wd.find_elements_by_class_name('pr')
    #print len(a), a, a[0].text
    if a == []:
        print 'error a', a
        return ('', 0, 0, 0, 0, 0)
    b = a[0].text.split()
    #print b
    if b == []:
        print 'error b', b
        return ('', 0, 0, 0, 0, 0)
    #print b
    curr = float(b[0])
    d = wd.find_elements_by_class_name('ch')[0].text.split()
    change = float(d[0])
    #print change
    d = wd.find_elements_by_class_name('snap-data')[0].text
    index = d.find('Open')
    d = d[index:].split()
    #print len(d), d
    if len(d) != 11:
        print 'error len a', len(d), d
        return ('', 0, 0, 0, 0, 0)     
    name = code
    #print d[:5]
    openprice = float(d[1])
    lastclose = curr - change
    todayhigh = todaylow = 0
    print 'GOOGLE Quote!',(name, openprice, lastclose, curr, todayhigh, todaylow)
    return (name, openprice, lastclose, curr, todayhigh, todaylow)  
   
   
def get_us_rt_price_GoogleWeb_Requests(code):
    url = 'http://www.google.com/finance?q=%s' % code
    print url, '---------------------------------------------'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=15,headers=headers)
        data = r.content
        print r.encoding
        r.close()
    except Exception, e:
        return []   
   
def get_us_rt_price(code):
    return get_us_rt_price_GoogleWeb(code)
   
#['market','code','name','price','ppk_limit']            
def stockmon_check_cn_stock(force):
    global cn_market_open
    strout = ''
    if not force and cn_market_open == check_cn_market_open() and cn_market_open == False:
        return ''
    if cn_market_open != check_cn_market_open():
        cn_market_open = check_cn_market_open()
        if not cn_market_open:
            wlist_save()
            force = True
        else:
            force = True
    #get time
    timetext = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
    if not cn_market_open:
        timetext += 'Close'
    timetext += '\n'
    #check list
    wlist_stock  = wlist_getlist()
    need_printout = False
    for one in wlist_stock:
        #print one
        if one[0] != 'cn':
            continue
        name, openprice, lastclose, curr, todayhigh, todaylow = get_cn_rt_price(one[1])
        if stockmon_debug:
            strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            strout += '%s: %s, %s, %s%%\n' %(name,curr, (curr-lastclose), day_chg_pct)
            one[2] = '%s'% name.encode('gbk')
            need_printout = True
        elif one[3] != curr and lastclose != 0:
            price_old = float(one[3])
            if price_old == 0.0:
                price_old = 0.1
            diff_ppk = 0
            if price_old:
                diff_ppk = abs((curr - price_old)*1000/price_old)
            day_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            #print diff_ppk, day_chg_pct
            if diff_ppk >= one[4] or stockmon_debug:
                need_printout = True
                one[2] = '%s'% name.encode('gbk')
                one[3] = curr
                strout += '%s: %s, %s, %s%%\n' %(name,curr, (curr-lastclose), day_chg_pct)
    if need_printout:
        strout += timetext
    return strout

#['market','code','name','price','ppk_limit']            
def stockmon_check_us_stock(force):
    global us_market_open
    strout = ''    
    if not force and us_market_open == check_us_market_open() and us_market_open == False:
        return ''    
    if us_market_open != check_us_market_open():
        us_market_open = check_us_market_open()
        if not us_market_open:
            wlist_save()
            force = True
        else:
            force = True
    #get time
    timetext = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
    if not us_market_open:
        timetext += 'Close'
    timetext += '\n'
    #check list
    wlist_stock  = wlist_getlist()
    need_printout = False
    for one in wlist_stock:
        time.sleep(2)
        #print one
        if one[0] != 'us':
            continue
        name, openprice, lastclose, curr, todayhigh, todaylow = get_us_rt_price(one[1])
        if stockmon_debug:
            strout += str([name, openprice, lastclose, curr, todayhigh, todaylow])
        if force:
            day_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            strout += '%s: %s, %s, %s%%\n' %(name,curr, (curr-lastclose), day_chg_pct)
            one[2] = '%s'% name
            need_printout = True
        elif one[3] != curr and lastclose != 0:
            price_old = float(one[3])
            if price_old == 0.0:
                price_old = 0.1
            diff_ppk = 0
            if price_old:
                diff_ppk = abs((curr - price_old)*1000/price_old)
            day_chg_pct = 0
            if lastclose:
                day_chg_pct = round ((curr-lastclose)*100/lastclose, 2)
            #print diff_ppk, day_chg_pct
            #print diff_ppk
            if diff_ppk >= one[4] or stockmon_debug:
                need_printout = True
                one[2] = '%s'% name
                one[3] = curr
                strout += '%s: %s, %s, %s%%\n' %(name,curr, (curr-lastclose), day_chg_pct)
    if need_printout:
        strout += timetext
    get_us_rt_price_sohu_done()
    return strout    
  
def stockmon_init(): 
    wlist_load()
    banner = '*** Stockmon Daemon. v1.0.1. ' 
    banner += '_us_cn_'
    banner += '_google_quote_'
    banner += '\n'
    return banner    

def stockmon_exit():
    global wd
    if wd != None:
        wd.quit()
    return 'stockmon_exit'    
    
def stockmon_process(force = False):
    global start_time
    global update_interval_in_seconds
    global stockmon_force
    global run_1st
    if run_1st:
        force = True
        run_1st = False
    
    if force:
        stockmon_force = True
    # update ?
    curr_time = time.time()
    if stockmon_debug:
        print (curr_time - start_time)
    if not force and (curr_time - start_time) < update_interval_in_seconds:    #update intervals
        return ''
    start_time = curr_time
    # start to update
    #print 'stockmon_force', stockmon_force
    try:
        strout = stockmon_check_cn_stock(stockmon_force)
    except:
        strout = 'check cn stock except!'
    try:
        strout += stockmon_check_us_stock(stockmon_force)
    except:
        strout += 'check us stock except!'
    stockmon_force = False
    return strout
            
if  __name__ == '__main__':   
    print get_cn_rt_price('sh600036')
    while False:
        for one in us_list:
            print get_us_rt_price(one.upper())
            time.sleep(1)
        time.sleep(25)
        print '------------------'
    stockmon_init()
    #wlist_add(['us', 'amcn', 5])
    #wlist_add(['us', 'dang', 5])
    while True:
        str = stockmon_process(True)
        if str != '':
            print str
        time.sleep(10)
        print '.'
        
