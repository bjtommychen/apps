# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from lychee_gtalk_io import *
from lychee_utils_list import *

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')

stockmon_enable = True
stockmon_debug = False
start_time = time.time()
#code_list = ['sh600036', 'sh601328']
cn_market_open = False
update_interval_in_seconds = 10

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
#    print text, checkopen,
    return checkopen

def get_cn_rt_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
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
#            return (name, "%-5s" % float(data[1]), "%-5s" % float(data[2]), "%-5s" % float(data[3]), 
#                    "%-5s" % float(data[4]), "%-5s" % float(data[5]))
            return (name, float(data[1]), float(data[2]), float(data[3]), 
                     float(data[4]), float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)    

#['market','code','name','price','ppk_limit']            
def stockmon_check_cn_stock():
    global cn_market_open      
    strout = ''    
    if cn_market_open != check_cn_market_open():
        cn_market_open = check_cn_market_open()
        if not cn_market_open:
            wlist_save()
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
        if one[3] != curr and lastclose != 0:
            price_old = float(one[3])
            if price_old == 0.0:
                price_old = 0.1
            diff_ppk = abs((curr - price_old)*1000/price_old)
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
    
def stockmon_init():
    wlist_load()
    
def stockmon_process():
    global start_time
    global update_interval_in_seconds
    # update ?
    curr_time = time.time()
    if stockmon_debug:
        print (curr_time - start_time)
    if (curr_time - start_time) < update_interval_in_seconds:    #update intervals
        return ''
    start_time = curr_time
    # start to update
    strout = stockmon_check_cn_stock()
    return strout
            