import os
import stat,fnmatch
import time
import sys
import stat,fnmatch
import csv
import numpy as np

# import matplotlib.pyplot as plt
# from pandas import DataFrame, Series

from mysql_access import *

reload(sys) 
sys.setdefaultencoding('utf')

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

def GetSimpleDayPriceList(code):
    cmd1 = "SELECT date_format(date, '%%Y-%%m-%%d'), close FROM `gpday` WHERE `code` LIKE \'%s\' and TIMESTAMPDIFF(month,date,now()) < 4 ORDER BY `date` DESC "
    cmd_run = cmd1 % code
    listout = list(mysql_execute(cmd_run))
    # print code, len(listout)
    return listout

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
    
DIFF_PCT_LIMIT = 0.5
DIFF_ABSPCT_LIMIT = 2.5
LATENT_PCTUP_LIMIT_PERDAY = 0.5
LATENT_DAYS_LIMIT = 40
   
def UpdateSidewaysStartDay(day_startLatent, theday, diff_pct, diff_pct_abs, prevdays):
    if day_startLatent == []:
        return [theday, diff_pct, diff_pct_abs, prevdays]
    # elif abs(diff_pct) < abs(diff_pct) or abs(diff_pct) < 1:
        # if diff_pct_abs < day_startLatent[2]:
            # return [theday, diff_pct, diff_pct_abs, prevdays]
    elif abs(diff_pct) < DIFF_PCT_LIMIT and diff_pct_abs < DIFF_ABSPCT_LIMIT:
        return [theday, diff_pct, diff_pct_abs, prevdays]
    return day_startLatent
    
MAX_DAYS = (80)
MIN_DAYS = (20)
# recent day at beginning
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
     
        
def CheckAllSideway_db():
    print 'Days range:', MIN_DAYS, '-', MAX_DAYS
    i = 0
    total = 0
    listr = []
    # timestamp_prev30days = (time.time()-3600*24*30)
    cnlist = mysql_GetStockList()
    for onecn in cnlist:
        total += 1
        code, name, volume = onecn
        if 'SH60' not in code and 'SZ00' not in code and 'SZ30' not in code:
            continue
        slist = GetSimpleDayPriceList(code)
        # print 'slist ', len(slist), slist[:5]
        day_startLatent, dayend = AnalyseDayList(slist)
        if day_startLatent == []:
            continue
        # [theday, diff_pct, diff_pct_abs, prevdays]
        if day_startLatent[3]>= LATENT_DAYS_LIMIT and day_startLatent[1] <= DIFF_PCT_LIMIT and day_startLatent[2] <= DIFF_ABSPCT_LIMIT:
            if day_startLatent[0][1] < dayend[1]:   # 总体上涨而不是下降
                # 限定已有的涨幅 < 40%, 
                if ((dayend[1] - day_startLatent[0][1])*100/day_startLatent[0][1])/day_startLatent[3] > LATENT_PCTUP_LIMIT_PERDAY:
                    continue
            timestamp_dayend = time.mktime(time.strptime(dayend[0], '%Y-%m-%d'))
            # print timestamp_dayend , timestamp_prev30days
            # if timestamp_dayend < timestamp_prev30days:
                # continue
            print code,name, day_startLatent, dayend
            listr.append(['cn', code, str(int(volume))+'Y', 'sideway'])
            i+=1
        # if i>10:
            # break
    print 'total', total, ', cnt', i
    # print listr
    save2csv('Sideway_cn.csv', listr)
    
########################################################################
if __name__ == '__main__':
    print 'Start ... '
    print (' Sideways Latent '.center(79, '-'))
    mysql_connect('192.168.99.9')
    mysql_setdebug(False)
    CheckAllSideway_db()
    mysql_disconnect()
    print 'End!'    