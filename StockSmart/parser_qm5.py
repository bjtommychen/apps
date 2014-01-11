# -*- coding: utf-8 -*

import sys
import os
import struct
import csv
import stat,fnmatch
import profile
import time
from ggplot import *
from pandas import DataFrame, Timestamp

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')
# sys.setdefaultencoding('ascii')

rblist = []
rblist2 = []
    
def get_Long(fp):
    num = struct.unpack("L",fp.read(4))
    return int(num[0])

def get_Float(fp):
    num = struct.unpack("f",fp.read(4))
    return float('%.2f' % num[0])
#    return struct.unpack("f",fp.read(4))[0]

def get_String12(fp):
    try:
        num = struct.unpack("12s",fp.read(12))
        return '%s' % num
    except:
        return ''

def get_DateString(m_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time))

###############################################
#### GET PATH
###############################################
Use_MemDrv = False
def get_Path(path):
    if Use_MemDrv:
        return 'm:/' + path
    else:
        return path

###############################################
#### GET ONE RECORD
###############################################
def get_OneRecord(fp, code_filter = ''):
    code = get_String12(fp)
    if code == '':
        return 0, 0, 0
    name = get_String12(fp)
    items = get_Long(fp)
    print 'code:',code, 'name:',name, 'Items:',items, '...',
    if code_filter != '' and code_filter not in code:
        fp.seek(items*(8*4), 1)
        return code, name, 0
    list5min = []
    for i in xrange(items):
        m_time = struct.unpack("L",fp.read(4))[0]
        m_fOpen = struct.unpack("f",fp.read(4))[0]
        m_fHigh = struct.unpack("f",fp.read(4))[0]
        m_fLow = struct.unpack("f",fp.read(4))[0]
        m_fClose = struct.unpack("f",fp.read(4))[0]
        m_fVolume = struct.unpack("L",fp.read(4))[0]
        m_fAmount = struct.unpack("L",fp.read(4))[0]
        m_fNull = struct.unpack("L",fp.read(4))[0]
        
            #format
        if True:
            m_fOpen = float('%.2f' % m_fOpen)
            m_fHigh = float('%.2f' % m_fHigh)
            m_fLow = float('%.2f' % m_fLow)
            m_fClose = float('%.2f' % m_fClose)
                    
#        print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time))
        line = (m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull)
#        print line
        list5min.append(line) 
    print 'done!'
    return code, name, list5min


def get_OneRecordSpecified(fp, code_filter = ''):
    while True:
        code = get_String12(fp)
        if code == '':
            return 0, 0, []
        name = '%s' % struct.unpack("12s",fp.read(12))
        items = struct.unpack("L",fp.read(4))[0]
#         print code, name, items
        if code_filter != '' and code_filter not in code:
            fp.seek(items*(8*4), 1)
#            print '.',
            continue
        list5min = []
        for i in xrange(items):
            m_time = struct.unpack("L",fp.read(4))[0]
            m_fOpen = struct.unpack("f",fp.read(4))[0]
            m_fHigh = struct.unpack("f",fp.read(4))[0]
            m_fLow = struct.unpack("f",fp.read(4))[0]
            m_fClose = struct.unpack("f",fp.read(4))[0]
            m_fVolume = struct.unpack("L",fp.read(4))[0]
            m_fAmount = struct.unpack("L",fp.read(4))[0]
            m_fNull = struct.unpack("L",fp.read(4))[0]
            

    #        print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time))
            line = (m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull)
#             print line
            list5min.append(line) 
        return code, name, list5min
    return 0, 0, 0

def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num    

def QM5_parserAll(filename, code_filter = ''):
    print 'QM5_parserAll', filename
    fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    num = 0
    while True:
        code, name, lists = get_OneRecord(fp, code_filter)
        if code == 0:
            break
        print 'Got', code, name, len(lists)
        for line in lists:
            m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
            print get_DateString(m_time),'   ', m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
        num += 1
    print num


def QM5_CheckAll(filename, code_filter = ''):
    cnt_total = 0
    cnt_missed = 0
    k_list = []

    print 'QM5_CheckAll', filename
    fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    num = 0
    last_mtime = 0
    while True:
        code, name, lists = get_OneRecord(fp, code_filter)
        if code == 0:
            break
        print 'Got', code, name, len(lists)
        linecnt = 1
        for line in lists:
            m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
#             print get_DateString(m_time),'   ', m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
            if False:
                if last_mtime == 0:
                    last_mtime = m_time
                    print time.gmtime(m_time)
                    continue
                else:
                    minute = (m_time - last_mtime)/60
                    if (minute>4 and minute < 90):
                        cnt_total +=minute
                        cnt_missed += (minute-5)
                        print minute, get_DateString(last_mtime), get_DateString(m_time)
                    last_mtime = m_time
            if False:
                if last_mtime == 0:
                    last_mtime = m_time
                    ts = time.gmtime(m_time)
                    print ts, type(ts), time.localtime(m_time)
                    nextday_mtime = m_time - ts.tm_hour*3600 - ts.tm_min*60 - ts.tm_sec
                    print 'init',get_DateString(m_time), get_DateString(nextday_mtime)
                    continue
                else:
#                     print time.ctime(m_time),  time.ctime(nextday_mtime)
                    if ( m_time < nextday_mtime ):
#                         print '<'
                        continue
#                     print '???',get_DateString(m_time), get_DateString(nextday_mtime)

                    if (m_time > nextday_mtime and m_time < (nextday_mtime + 24*3600)):
#                         print 'inner goto nextday'
                        nextday_mtime += 24*3600
                    else:
#                         print '>'
#                         print 'skip some day?'
                        test_mtime = nextday_mtime
                        ts = time.gmtime(m_time)
                        mtime_clock0 = m_time - ts.tm_hour*3600 - ts.tm_min*60 - ts.tm_sec
                        while (test_mtime < mtime_clock0):
                            if time.gmtime(test_mtime).tm_wday < 5:
                                print '----',get_DateString(test_mtime), time.gmtime(test_mtime).tm_wday
                            test_mtime += 24*3600
                        nextday_mtime = test_mtime
            if True:
                row = linecnt, m_fOpen, m_fHigh, m_fLow, m_fClose
                #, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
                if linecnt > (len(lists) - 100): 
                    k_list.append(row)
                
            linecnt += 1
        print 'total item ', len(k_list)
        print 'item per line', len(k_list[1])
#         print k_list
        powd = DataFrame(k_list, columns=['date', 'open','high','low','close'])
#         print ggplot(aes(x='date', y='open'), data=powd) + \
#             geom_point(color='lightblue') + \
#             geom_line(alpha=0.25) + \
#             stat_smooth(span=.05, color='black') + \
#             ggtitle("Power comnsuption over 13 hours") + \
#             xlab("Date") + \
#             ylab("Open")
        meat_lng = pd.melt(powd[['date', 'open', 'high', 'low']], id_vars='date')
        print ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
            geom_point(size =3) + \
            stat_smooth(color='red')            
        num += 1
    print num
    print cnt_missed, cnt_total

def QM5_parserOne(filename, code_filter = ''):
    fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    print '0x%08x' % flag, '0x%08x' % version, '0x%08x' % total_num
    
    code, name, list5min = get_OneRecordSpecified(fp, code_filter)
    print code, name, len(list5min)
#     print list5min
    
    
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

def get_AllQMdata_for_one(ext, filter = 'SH600036'):
    dirlist = getFileList('qm5_data/', ext, subdir = False)
    listall = []
    for filename in dirlist:
        print filename  
        fp=open(filename,"rb")
        flag, version, total_num = get_QM_header(fp)
        print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
        code, name, list5min = get_OneRecordSpecified(fp, filter)
        print code, name, len(list5min)
        if len(list5min):
            listall += list5min
        fp.close()
    print 'Total', len(listall)
    print 'start sorting ... '
    listall.sort(key=lambda data : data[0], reverse=False)
    print 'sorted.'
    write_QM_data('test.qm5', code, name, listall)
#    print listall
#    

def write_QM_data(filename, code, name, listall):
    print 'write_QM_data', filename
    fp=open(filename,"wb")
    flag = 0xffffffe1
    version = 0x19730101
    total_num = len(listall)
    fp.write(struct.pack("L",flag))
    fp.write(struct.pack("L",version))
    fp.write(struct.pack("L", 1))
    fp.write(struct.pack("12s",code))
    fp.write(struct.pack("12s",name))
    fp.write(struct.pack("L",total_num))
    for line in listall:
#        print line
        fp.write(struct.pack("LffffLLL",line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7]))
    fp.close()
#     QM5_parserAll(filename)


# 怎么回事
def reformat_history_csv(codename):
    filename = 'data/'+codename+'.csv'
    filename_out = 'temp/'  + codename+'_out.csv'
    
    if os.path.exists(filename_out): 
        print 'skip reformat ',   
        return
    
    reader = csv.reader(file(filename,'rb'))
    i = 0
    k_list = []
    listall = []
    print '\nread ...'
    for row in reader:
        if i ==0:
            i = 1
            continue
        listall.append(row)
    print len(listall), len(listall[0])
    print 'sort ...'    
    listall.sort(key=lambda data : data[0], reverse=False)
    i = 1
    print 'No. Date    Open    High    Low    Close    Volume    Adj Close'
    for row in listall:
        if (len(row) < 7 or float(row[5]) == 0): #check Volume==0 row.
            continue
        line = []
        line.append(i)
        for j in range(0, len(listall[0])):
            line.append(row[j])
#         print line
        k_list.append(line)
        i += 1
    listall = []
    
    print 'write sorted data to csv ...'
    if True:
        fcsv = open(filename_out, 'wb')
        csvWriter = csv.writer(fcsv)
        for row in k_list:
            csvWriter.writerow(row)
        fcsv.close()
    print 'string to float ...'
    for row in k_list:
        if (len(row) == 8):
            line = int(row[0]), row[1], float(row[2]), float(row[3]), float(row[4]), float(row[5]), int(row[6]), float(row[7])
            listall.append(line)

    print 'ggplot ...'
    if False:
        powd = DataFrame(listall, columns=['index','date', 'open','high','low','close','volume','adj'])
        print ggplot(aes(x='index', y='open'), data=powd) + \
            geom_point(color='lightblue') + \
            geom_line(alpha=0.25) + \
            stat_smooth(span=.05, color='black') + \
            ggtitle("Power comnsuption over 13 hours") + \
            xlab("Date") + \
            ylab("Open")
        meat_lng = pd.melt(powd[['index', 'high','low']], id_vars='index')
        print ggplot(aes(x='index', y='value', colour='variable'), data=meat_lng) + \
            geom_point(size =3) + \
            stat_smooth(color='red')   

# 检查在至少下跌pctDown情况下, 最多的反弹pct
def check_rebound_percent(codename,pctDown, pctRebound, pctDown2):
    filename_out = 'temp/' +codename+'_out.csv'
    reader = csv.reader(file(filename_out,'rb'))
    tHigh = tHighIdx = 0.
    tLow = tLowIdx = 0.
    tRebound = tReboundIdx = 0
    tReboundLow = tReboundLowIdx = 0
    mode = 0

    for row in reader:
        if (len(row) != 8):
            continue
        mIndex, mDate, mOpen, mHigh, mLow, mClose, mVolume, mAdj = row
        mIndex = int(mIndex)
        mHigh = float(mHigh)
        mLow = float(mLow)
        # init
#         print 'mIndex', mIndex
        if mode == 0:
#             print 'init'
            tHigh = mHigh
            tLow = mLow
            tHighIdx = mIndex
            tLowIdx = mIndex
            mode = 1
        # find peak
        elif mode == 1: 
            if mHigh > tHigh:   #Higher found
                tHigh = mHigh
                tHighIdx = mIndex
                tLow = mLow
                tLowIdx = mIndex
            if mLow < tLow:     #Lower found
                tLow = mLow
                tLowIdx = mIndex
            if tHighIdx >= tLowIdx:
                continue
            pct1 = (tHigh - tLow)*100./tHigh
            if pct1 > pctDown:
#                 print 'pct', pct, 'pctDown', pctDown
#                 print tHigh, tHighIdx, tLow, tLowIdx
                mode = 2
                tRebound = tLow
                tReboundIdx = tLowIdx
        # find bottom
        elif mode == 2:
            if mLow < tLow: #Lower found
                tLow = mLow
                tLowIdx = mIndex
                tRebound = tLow
                tReboundIdx = tLowIdx
            if mHigh > tRebound:    #Rebound higher
                tRebound = mHigh
                tReboundIdx = mIndex
            if tReboundIdx <= tLowIdx:
                continue
            pct2 = (tRebound - tLow)*100./tLow
            if pct2 > pctRebound:
                mode = 3
                tReboundLow = tRebound
                tReboundLowIdx = tReboundIdx
#                 print 'mode2',tReboundLowIdx, tReboundLow, tReboundIdx, tRebound
        elif mode ==3:
            if mHigh > tRebound:    #Rebound higher
                tRebound = mHigh
                tReboundIdx = mIndex
                tReboundLow = mLow
                tReboundLowIdx = mIndex
            if mLow < tReboundLow: #Lower found
                tReboundLow = mLow
                tReboundLowIdx = mIndex
#             print tReboundLowIdx, tReboundLow, tReboundIdx, tRebound
            if tReboundLowIdx <= tReboundIdx:
                continue
            pct2 = (tRebound - tReboundLow)*100./tRebound
            if pct2 > pctDown2:
                mode = 4                         
        elif mode == 4:
            pct1 = float('%.2f' % ((tHigh - tLow)*100./tHigh))
            pct2 = float('%.2f' %((tRebound - tLow)*100./tLow))
            if False:   
                print ' -------------- Rebound  -----------------'
                print ' ---- ', tHigh, tHighIdx, '-(',  (tLowIdx - tHighIdx), pct1, '%', ')-', tLow, tLowIdx, '-(', (tReboundIdx - tLowIdx), pct2,'%', ')-', tRebound, tReboundIdx
                print ' ---------------------------------------------------'
            mode = 0
#             line = tHighIdx, tHigh
#             rblist.append(line)
#             line = tLowIdx, tLow
#             rblist.append(line)            
#             line = tReboundIdx, tRebound
#             rblist.append(line)            
#             line = tReboundLowIdx, tReboundLow
#             rblist.append(line)
            global rblist2
#             print mDate, pct1, pct2
            year = int(mDate.split('-')[0])
#             line = pct1, pct2, year
#             if 1 < pct1 < 50 and 1 < pct2 < 50 and year > 2010:
            line = pct1, (tLowIdx - tHighIdx), year
            rblist2.append(line)

def rebound_list_draw():
    if True:
        global rblist2
        print rblist2
        powd = DataFrame(rblist2, columns=['index','open','year'])
        print ggplot(aes(x='index', y='open'), data=powd) + \
            geom_point(color='lightblue', size = 9) + \
            ggtitle("Rebound") + \
            xlab("Date") + \
            ylab("Open")
            
def check_rebound_all():
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    for row in reader:
        codename = row[0]
#         if '600036' not in codename:
#             continue
        print 'code:', codename
        reformat_history_csv(codename)
        check_rebound_percent(codename,10,5,3)
                
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
if  __name__ == '__main__':
    
    start = time.time()
    print 'main start!'

#    QM5_parser('Quote.QM5')
#    QM5_parser('qm5_data/5F201307.QM5')
#    QM5_parserOne('qm5_data/201307.QM1')
#    QM5_parserOne('qm5_data/201307.QM1')
#     QM5_CheckAll( get_Path('input/SH600036.qm5'))

#     get_AllQMdata_for_one('*.qm5', 'SH600036')

#     reformat_history_csv('600036')
#     check_rebound_percent('600036',20,10,5)
    check_rebound_all()
    rebound_list_draw()
#     check_rebound_percent('600036',10,5,2.5)
    print 'done!'
    end = time.time()
    elapsed = float('%.2f' %(end - start))
    print "Time taken: ", elapsed, "seconds."
