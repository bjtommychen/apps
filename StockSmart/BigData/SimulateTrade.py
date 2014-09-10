# -*- coding: utf-8 -*
import time, datetime
import sys
import os
import math
import csv
import stat,fnmatch
import struct
import argparse  
from pandas import DataFrame, Series
import pandas as pd

from QMdata_Getby import *

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')


def get_DateString(m_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time))

def get_TimeFromString(time_string):
    return time.mktime(time.strptime(time_string, '%Y-%m-%d %H:%M:%S'))-time.timezone    
    
# Trader Warehouse
mycash = 0
myhold=[]
mytotal_yesterday = 0

def myhold_init(value):
    global mycash
    global myhold
    global mytotal_yesterday
    mycash = value
    myhold = []
    mytotal_yesterday = value   
    print 'init. mycash', value

def myhold_get_cashsize():
    global mycash
    global myhold
    print 'mycash', mycash
    return mycash

def myhold_getsize():
    global myhold
    return len(myhold)
    
def myhold_listall():
    global mycash
    global myhold
    global mytotal_yesterday    
    market_value = 0    
    print '*************** list ****************'
    index = 1
    for code,price,amount, codename in myhold:
        if (code and price and amount):
            print 'No.',index, ':',code, price, amount, codename
            market_value = market_value + price*amount
            index += 1
    total_yesteray =  mytotal_yesterday
    mytotal_yesterday = int(mycash + market_value)
#    return int(mycash), mytotal_yesterday,  mytotal_yesterday - total_yesteray
    print 'Cash:', int(mycash), ', Total:', int(mycash + market_value), 'Gain/Loss:', mytotal_yesterday - total_yesteray
    print '*************************************'
        
def myhold_buy(code, price, amount, name = None):
    global mycash
    global myhold
    if ((price*amount)*1.002) < mycash:
        line = (code, price, amount, name)
        myhold.insert(0, line)
        mycash = mycash - (price*amount)*(1. + 0.002)
        print 'Buy', line, name
    else:
        print 'buy, out of cash!'

def myhold_sell(code, price, sell_amount, name = None):
    global mycash
    global myhold
    for i in range(0,len(myhold)):
        if myhold[i][0] == code:
            code, buyprice,amount, name = myhold[i]
            print 'Sell', code, price, sell_amount, name
            if sell_amount <= amount:
                mycash = mycash + price*sell_amount*(1. - 0.002)
                if  sell_amount < amount:
                    line = (code, buyprice, amount - sell_amount, name)
                    del myhold[i]
                    myhold.insert(0, line)                    
                else:
                    del myhold[i]
                return
    print 'sell failed.'  

def DoSimulateCatchSpurt():
    df = pd.read_csv('top100.csv')#, skiprows=[0])
    code_lists = list(df['code'])
    #code_lists = ['SH600036','SH601012','SH601996','SH601519','SH601038','SH603128','SH603002','SH601789','SH601118','SH601901']
    print code_lists
    filedata = 'bigdata_merge\MergeAll.qm'
    strStart = '2014-03-03 09:31:00'
    strStop  = '2014-06-03 09:31:00'
    
    bNeedInit = True
    myhold_init(100000)
    timeDayStart = get_TimeFromString(strStart)
    lastclose = []
    while True:
        print 'Day:', get_DateString(timeDayStart)
        gmtime = time.gmtime(timeDayStart)
        if (datetime.datetime(gmtime.tm_year,gmtime.tm_mon,gmtime.tm_mday).weekday() > 4):
            print 'Skip weekend.'
            timeDayStart += (24*60*60)
            continue
        if get_DateString(timeDayStart) == strStop:
            break
        #Sell if had
        if myhold_getsize():
            global myhold
            timeMin = timeDayStart + ((25-1)*60)
            print 'Prepare sell at', get_DateString(timeMin)
            myhold_copy = myhold[:]
            for code,price,amount, codename in myhold_copy:
                if (code and price and amount):
                    print code,price,amount
                    r=QM5_GetListByDate(args.filename, [code], get_DateString(timeMin))
                    if r != []:
                        one = r[0]; code, name, line = one
                        m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line                
                        myhold_sell(code, m_fClose, amount, codename)
            myhold_listall()
            print 'Sell done.'
            
        #Get Day minutes
        bBuyStock = False
        BuyCount = 0
        for m in range(5, 35):
            if lastclose == []:
                break
            if BuyCount > 10:
                break
            timeMin = timeDayStart + ((m-1)*60)
            #print '\t', m, get_DateString(timeMin)
            r=QM5_GetListByDate(args.filename, code_lists, get_DateString(timeMin))
            for one in r:
                code, name, line = one
                m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
                #print code, name, get_DateString(line[0]), line
                for one_close in lastclose:
                    code_close, name_close, m_fClose_close = one_close
                    if code == code_close:
                        pct = ((m_fClose - m_fClose_close)*100.0/m_fClose_close)
                        #print pct
                        if pct>=3 and pct<4.5:
                            print 'buy', code, name, 'change%', pct, 'at', get_DateString(m_time)
                            myhold_buy(code, m_fClose, int(10000/m_fClose), name)
                            lastclose.remove(one_close)
                            bBuyStock = True
                            BuyCount += 1
                        
        #Get close
        timeMin = timeDayStart + ((330-1)*60)
        #print '\t', get_DateString(timeMin)
        r=QM5_GetListByDate(args.filename, code_lists, get_DateString(timeMin))
        if r != []:
            lastclose = []
            for one in r:
                code, name, line = one
                m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
                #print code, name, get_DateString(line[0]), m_fClose
                line = code, name, m_fClose
                lastclose.append(line)      
            
        timeDayStart += (24*60*60)
        if myhold_getsize() and bBuyStock:
            myhold_listall()
        #str = raw_input('Press to continue .... ')

def DoSimulateTest():
    myhold_init(500000)
    myhold_buy('SH600036', 10, 1000, '36')
    myhold_buy('SH600016', 8, 1000, '16')
    myhold_buy('SH600026', 10, 1000)
    myhold_listall()
    myhold_sell('SH600036', 12, 80, '36')
    myhold_listall()
    
#Ö÷º¯Êý  
if  __name__ == '__main__':
    print '#'*60
    print '##### Simulater. ²âÊÔ°æ'
    print '#'*60
    print 'Config:'

    parser = argparse.ArgumentParser()
    #parser.add_argument('-t', action='store', dest='taskid', default='-1', help='Specify the task id.')
    parser.add_argument('--filter', action='store', dest='filter', default='', help='Specify the filter, for example SH600036.')       
    parser.add_argument('-i', action='store', dest='filename', default='bigdata_merge\MergeAll.qm', help='Specify the QM1/QM5 data file to read.')       
    parser.add_argument('--show_detail', action='store_true', dest='detail',default=False,help='print minute data.') 
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s v1.0')
    args = parser.parse_args()

    DoSimulateCatchSpurt()
    
    print 'Completed !'    