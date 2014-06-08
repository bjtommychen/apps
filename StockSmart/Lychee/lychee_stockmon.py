# -*- coding: utf-8 -*
import time
import sys
import os
import urllib, urllib2
from lychee_gtalk_io import *

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')

stockmon_enable = True
stockmon_debug = True
start_time = time.time()
code_list = ['sh600036', 'sh601328']


def stockmon_process_cmds(cmds):
    print 'stockmon_process_cmds', cmds
    str = ''
    if (len(cmds) == 0):
        str += 'stockmon help - for more.'
    else:    
        if cmds[0] == 'help' or cmds[0] == '?':
            str += 'stockmon help:\n'+ \
                '\thelp - print help \n'+\
                '\ton - stockmon on \n' +\
                '\toff - stockmon off \n' +\
                '\tdebug - stockmon debug mode \n' +\
                ''
        if cmds[0] == 'on':
            stockmon_enable_send(True)
            str += 'stockmon set on.'
        if cmds[0] == 'off':
            stockmon_debug = False
            stockmon_enable_send(False)
            str += 'stockmon set off.'
        if cmds[0] == 'debug':
            stockmon_debug = True
            str += 'stockmon set debug on.'

            
    return str

def stockmon_enable_send(onoff):
    stockmon_enable = onoff        
    
def check_market_open():
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

def get_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
    try:
        req = urllib2.Request(url)
    #        req.set_proxy('proxy.XXX.com:911', 'http')
        content = urllib2.urlopen(req).read()
    except Exception, e:
        return ('', 0., 0, 0.)
    else:
        strs = content.decode('gbk')
        data = strs.split('"')[1].split(',')
        name = "%s" % data[0]
        if (name):
            price_current = "%-5s" % float(data[3])
            change_percent = ( float(data[3]) - float(data[2]) )*100 / float(data[2])
            change_percent = "%s" % round (change_percent, 2)
            return (name, float(price_current), float(float(data[3]) - float(data[2])), float(change_percent))
        else:
            return ('', 0., 0, 0.)    
    
def get_rt_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
    try:
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
    except Exception, e:
        return ('', 0., 0, 0.)
    else:
        strs = content.decode('gbk')
        data = strs.split('"')[1].split(',')
#        print data
        name = "%s" % data[0]
        if (name):
            return (name, "%-5s" % float(data[1]), "%-5s" % float(data[2]), "%-5s" % float(data[3]), 
                    "%-5s" % float(data[4]), "%-5s" % float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)    
    
def stockmon_process():
    price_old = 0.0
    market_open = False
    diff = False
    text = ''
    global start_time
    curr_time = time.time()
    if (curr_time - start_time) < 5:
        return ''
    start_time = curr_time
    try:
        index = 0
        
        if market_open != check_market_open():
            price_old = 0.
            market_open = check_market_open()
            
        text = ''
        #get time
        text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
        if not market_open:
            text += 'Close'
        text += '\n'
        print text
        #get price
        global code_list
        for code in code_list:
            name, price_current, price_diff, change_percent = get_price(code)
            if price_current == 0.:
                print 'get price failed!'
                break
            if index == 0:
                if price_old == 0.:
                    price_old = price_current
                    diff = True
                if price_current != price_old:
                    diff_ppk = abs((price_current - price_old)*1000/price_old)
#                        print 'diff_ppk is', diff_ppk,
                    diff = diff_ppk > 2
                if diff:
                    price_old = price_current
            text += '%s: %s, %s, %s%%' %(name,price_current, price_diff, change_percent)
            index += 1
        print text
    except KeyboardInterrupt:
        print 'Exception!'
    finally:
        if diff or stockmon_debug:
            return text
        else:
            return ''
            