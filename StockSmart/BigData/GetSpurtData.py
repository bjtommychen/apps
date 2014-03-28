import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import struct

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
# sys.setdefaultencoding('utf8')
sys.setdefaultencoding('gbk')

datapath = "output/"
ext="csv"

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
#            print fullname
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
    
def Get_AllSpurtData():
    dirlist = getFileList(datapath, '*.'+ext, subdir = False)
    listall = []
    fcsv = open("get_all_data.csv", 'wb')
    csvWriter = csv.writer(fcsv)
    
    for filename in dirlist:
        print 'Checking...', filename
        line  = Get_OneSpurtData(filename)
        print line
#         listall.append(line) 
        csvWriter.writerow(line)
    fcsv.close()
     

index = 0
def Get_OneDayData_Init():
    global index
    index = 0
    
def Get_OneDayData(lines):
    global index
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
    return daylines
    
def Get_OneSpurtData(filename):
    reader = csv.reader(file(filename,'rb'))
    alllines = []
    m_fLastClose = 0.0    
    for row in reader:
        alllines.append(row)
    print 'line', len(alllines)    
    cnt_days=0
    cnt_boom=0
    cnt_boom_failed=0
    Get_OneDayData_Init()            
    while(True):
        daylines = Get_OneDayData(alllines)
        if (daylines == []):
            break;
        cnt_days += 1
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        #init last close
        if m_fLastClose == 0.0:
            m_fLastClose = m_fClose
            continue
#         print 'Checking ', time_str
        #chec Boom
        max_price = m_fLastClose *1.095
        bHit = False
        for i in range(0, len(daylines)):
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[i]
            if m_fHigh > max_price and bHit == False:
#                 print "Boom! at", time_str, m_fLastClose, m_fHigh, i
                bHit = True
                cnt_boom += 1
                break
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        m_fLastClose = m_fClose
        if bHit ==True:
            if (m_fClose < max_price):
#                 print "Boom Failed !" ,m_fClose ,max_price
                cnt_boom_failed += 1
#     print cnt_days, cnt_boom, cnt_boom_failed, float('%.2f' % (float(cnt_boom)*100/cnt_days)), '%', float('%.2f' % (float(cnt_boom_failed)*100/cnt_boom)), '%'
    if cnt_days == 0:
        cnt_days = 1
    if cnt_boom == 0:
        cnt_boom = 1               
    line = filename, cnt_days, cnt_boom, cnt_boom_failed , float('%.2f' % (float(cnt_boom)*100/cnt_days)), float('%.2f' % (float(cnt_boom_failed)*100/cnt_boom))
    return line                
        
if  __name__ == '__main__':
    print 'Start !'
#     Get_OneSpurtData('output/SZ002041_qm1.csv')
    Get_AllSpurtData()
    print 'Completed !'
    