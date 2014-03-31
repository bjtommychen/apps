# -*- coding: utf-8 -*

import time
import sys
import os
import math
import csv

# print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
#reload(sys) 
# sys.setdefaultencoding('utf8')
# sys.setdefaultencoding('gbk')

data_path = "output/"
data_ext="csv"
bUseMultiCore = False
thread_num=8
threads = []

   
def Get_OneDayData(lines, index):
    daylines = []
    i = index
    count = 0
    while (i < len(lines)):
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = lines[i]
        m_time = int(m_time)
        m_fOpen = float(m_fOpen)
        m_fHigh = float(m_fHigh)
        m_fLow = float(m_fLow)
        m_fClose = float(m_fClose)
        m_fVolume = int(m_fVolume)
        m_fAmount = int(m_fAmount)
        wline = time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
        daylines.append(wline)
        count += 1
        i += 1
        if (count >= 240) or time_str.find('15:00:00') != -1:
            break;
    index = i
#     print 'index', index
    return index, daylines


#获取涨停的百分比的数据    
def Get_SpurtDayCount(filename):
    reader = csv.reader(file(filename,'rb'))
    alllines = []
    m_fLastClose = 0.0    
    for row in reader:
        alllines.append(row)
    code,name,cnt = alllines[0]    
    cnt_days=0
    cnt_boom=0
    cnt_boom_failed=0
    index = 1   # skip 1st line.
    while(True):
        index, daylines = Get_OneDayData(alllines, index)
        if (daylines == []):
            break;
        cnt_days += 1
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        #init last close
        if m_fLastClose == 0.0:
            m_fLastClose = m_fClose
            continue
        #check Boom
        max_price = m_fLastClose *1.095
        bHit = False
        for i in xrange(0, len(daylines)):
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[i]
            if m_fHigh > max_price and bHit == False:
#                 print "Boom! at", time_str, m_fLastClose, m_fHigh, i
                bHit = True
                cnt_boom += 1
                break
        if bHit ==True:
            if (m_fClose < max_price):
#                 print "Boom Failed !" ,m_fClose ,max_price
                cnt_boom_failed += 1
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        m_fLastClose = m_fClose
        
    if cnt_days == 0:
        cnt_days = 1
    if cnt_boom == 0:
        cnt_boom = 1               
    print code, name, cnt_days, cnt_boom, cnt_boom_failed , float('%.2f' % (float(cnt_boom)*100/cnt_days)), float('%.2f' % (float(cnt_boom_failed)*100/cnt_boom))
    

#获取涨停的时间段的数据    
def Get_SpurtStartTime(filename):
    reader = csv.reader(file(filename,'rb'))
    alllines = []
    m_fLastClose = 0.0    
    for row in reader:
        alllines.append(row)
    code,name,cnt = alllines[0]    
    cnt_days=0
    cnt_boom=0
    cnt_boom_failed=0
    index = 1   # skip 1st line. it's info line.
    while(True):
        index, daylines = Get_OneDayData(alllines, index)
        if (daylines == []):
            break;
        cnt_days += 1
        #init last close
        if m_fLastClose == 0.0:
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
            m_fLastClose = m_fClose
            continue
        #check Boom
        max_price = m_fLastClose *1.095
        bHit = False
        for i in xrange(0, len(daylines)):
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[i]
            if i == 0:
                timeDayStart = m_time
            if m_fHigh > max_price and bHit == False:   #当日初次涨停
                timeSpurt = m_time - timeDayStart
                bHit = True
                cnt_boom += 1
                break
        if bHit ==True:
            if (m_fClose < max_price):  #涨停失败
                cnt_boom_failed += 1
            print code, name, cnt_days, time_str, timeSpurt/60
        #save lastclose price    
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]            
        m_fLastClose = m_fClose

#获取涨停失败后低点的相对于昨天收盘价的涨的百分数, 主要是为了推断可能的亏损点, 利于计算买入点. 
def Get_SpurtLowWhenFailed(filename):
    reader = csv.reader(file(filename,'rb'))
    alllines = []
    m_fLastClose = 0.0    
    for row in reader:
        alllines.append(row)
    code,name,cnt = alllines[0]    
    cnt_days=0
    cnt_boom=0
    cnt_boom_failed=0
    index = 1   # skip 1st line. it's info line.
    while(True):
        index, daylines = Get_OneDayData(alllines, index)
        if (daylines == []):
            break;
        cnt_days += 1
        #init last close
        if m_fLastClose == 0.0:
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
            m_fLastClose = m_fClose
            continue
        #check Boom
        max_price = m_fLastClose *1.095
        bHit = False
        for i in xrange(0, len(daylines)):
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[i]
            if m_fHigh > max_price and bHit == False:   #当日初次涨停
                bHit = True
                idx_boom = i
                break
        if bHit ==True:
            if (m_fClose < max_price):  #涨停失败
                cnt_boom_failed += 1
            print code, name, cnt_days, time_str, timeSpurt/60
        #save lastclose price    
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        m_fLastClose = m_fClose


def Do_dataJob(filename):   #任务调度
#     Get_SpurtDayCount(filename)
    Get_SpurtStartTime(filename)
#     Get_SpurtLowWhenFailed(filaname)
        
if  __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(0)
#     print 'Start !'
    start = time.time()
#     print 'Checking ', sys.argv[1]
    Do_dataJob(sys.argv[1])   
    end = time.time()
    elapsed = float('%.2f' %(end - start))
#     print "Time taken: ", elapsed, "seconds."
#     print 'Completed !'
    