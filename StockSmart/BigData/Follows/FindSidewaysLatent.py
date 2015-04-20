import os
import stat,fnmatch
import time
import sys
import stat,fnmatch
import subprocess
import multiprocessing
import csv
import numpy as np

import matplotlib.pyplot as plt
from pandas import DataFrame, Series

def save2csv(fname, lista):
    fcsv = open(fname, 'wb')
    csvWriter = csv.writer(fcsv)
    csvWriter.writerows(lista)
    fcsv.close()
        
def loadfromecsv(fname):
    lista = []
    reader = csv.reader(file(fname,'rb'))
    for line in reader:        
        lista.append(line)
    return lista

def external_cmd(cmd, rundir='./', msg_in=''):
    # print 'rundir:',rundir, ', cmds:', cmd
    # return 'stdout', 'stderr'
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   cwd=rundir
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        # time.sleep(0.2)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            # print fullname
            st = os.lstat(fullname)
            if stat.S_ISDIR(st.st_mode) and subdir:
                dirlist += getFileList(fullname,ext)
            elif os.path.isfile(fullname):
                if fnmatch.fnmatch( fullname, ext): 
                    dirlist.append(fullname)
                else:
                    pass
        return dirlist
    else:
        return [] 
    
def get_DateString(m_time):
    return str(time.strftime('%Y-%m-%d', time.gmtime(m_time)))

def get_TimeFromString(time_string):
    return time.mktime(time.strptime(time_string, '%Y-%m-%d'))-time.timezone       
    
def GetPriceDayList(filename):
    reader = csv.reader(file(filename,'rb'))
    daylist = []
    idx = 0
    for one in reader:
        idx += 1
        if idx == 1:
            continue
        m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = one
        m_fOpen = float(m_fOpen)
        m_fHigh = float(m_fHigh)
        m_fLow = float(m_fLow)
        m_fClose = float(m_fClose)
        m_fVolume = float(m_fVolume)
        m_fAmount = float(m_fAmount)
        wline = m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
        daylist.append(wline)
    daylist.sort(key=lambda data : data[0], reverse=True)
    return daylist

def GetSimpleDayPriceList(rawlist):
    listout = []
    for one in rawlist:
        m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = one
        listout.append([m_time,m_fClose])
    return listout

def UpdateSidewaysStartDay(day_startLatent, theday, diff_pct, diff_pct_abs, prevdays):
    if day_startLatent == []:
        return [theday, diff_pct, diff_pct_abs, prevdays]
    elif abs(diff_pct) < abs(diff_pct) or abs(diff_pct) < 1:
        if diff_pct_abs < day_startLatent[2]:
            return [theday, diff_pct, diff_pct_abs, prevdays]
    return day_startLatent

def GetSidewaysData(listd):
    length = len(listd)
    dayend = listd[0]
    daystart = listd[-1]
#     print daystart, dayend
    prices = []
    for one in listd:
        prices.append(one[1])
    price_mean = np.mean(prices)
    diff_startend_mean = (dayend[1]-daystart[1])/length
    i = 0
    diff_total = 0
    diff_total_abs = 0
    for one in listd:
        value_centerd = dayend[1] - diff_startend_mean*i
        diff_total += (one[1] - value_centerd)
        diff_total_abs += abs((one[1] - value_centerd))
        i+=1
    diff_pct = round(diff_total*100/length/dayend[1], 3)
    diff_pct_abs = round(diff_total_abs*100/length/dayend[1], 3)
#     print diff_pct, '%,', diff_pct_abs, '%'
    return (diff_pct, diff_pct_abs)
#     print  diff_total_abs/length
    
    
MAX_DAYS = (80)
MIN_DAYS = 20
def AnalyseDayList(daylist):
    if len(daylist)< MIN_DAYS:
        return [],[]
    max_days = min(MAX_DAYS, len(daylist))
    day_startLatent = []
#     print 'Days range', MIN_DAYS, '-', max_days
    for prevdays in xrange(MIN_DAYS, max_days):
        listd = daylist[:prevdays]
#         print '-'*8, ' Days',len(listd), get_DateString(listd[-1][0]) 
        diff_pct, diff_pct_abs = GetSidewaysData(listd)
        day_startLatent = UpdateSidewaysStartDay(day_startLatent, listd[-1], diff_pct, diff_pct_abs, prevdays)
#         print day_startLatent
    return day_startLatent, daylist[0]
     
        
def CheckAll_InPath(inpath = "./output_qda"):
    # inpath = "d:\\workspace\\apps\\StockSmart\\BigData\\Follows\\output_qda\\"
    print inpath
    print 'Days range:', MIN_DAYS, '-', MAX_DAYS
    filelist = getFileList(inpath, "*.csv", False)
    print 'filelist', len(filelist)
    i = 0
    total = 0
    listr = []
    for fname in filelist:
        total += 1
        if 'SH60'not in fname and 'SZ00' not in fname and 'SZ30' not in fname:
            continue
        daypricelist = GetPriceDayList(fname)
#     print len(list), list[:3], get_DateString(list[0][0]) 
        slist = GetSimpleDayPriceList(daypricelist)
#     print 'slist ', len(slist), slist[:5]
        day_startLatent, dayend = AnalyseDayList(slist)
        if day_startLatent == []:
            continue
#         print day_startLatent
        if day_startLatent[3]> 40 and day_startLatent[1] < 1 and day_startLatent[2] < 2.5:
            if day_startLatent[0][1] < dayend[1]:
                # 限定已有的涨幅
                if ((dayend[1] - day_startLatent[0][1])*100/day_startLatent[0][1]) > 30:
                    continue
            print fname[fname.find('output_qda\\'):], day_startLatent, dayend
            listr.append(['cn', fname[fname.find('output_qda\\'):][11:19]])
            i+=1
#         if i>10000:
#             break
    print 'total', total, 'cnt', i
    print listr
    save2csv('Sideway_cn.csv', listr)
    
########################################################################
if __name__ == '__main__':
    print 'Start ... '
    print (' Sideways Latent '.center(79, '-'))
    CheckAll_InPath()
    print 'End!'    