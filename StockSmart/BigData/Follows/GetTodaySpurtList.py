import os
import stat,fnmatch
import csv
import time
import sys
import os
import subprocess
import struct
import argparse

def save2csv(fname, list):
    fcsv = open(fname, 'wb')
    csvWriter = csv.writer(fcsv)
    csvWriter.writerows(list)
    fcsv.close()
    
def external_cmd(cmd, rundir='./', msg_in=''):
    print 'rundir:',rundir, ', cmds:', cmd
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
  
def get_Long(fp):
    num = struct.unpack("L",fp.read(4))
    return int(num[0])

def get_Float(fp):
    num = struct.unpack("f",fp.read(4))
    return float('%.2f' % num[0])

def get_String12(fp):
    try:
        num = struct.unpack("12s",fp.read(12))
        return '%s' % num
    except:
        return ''  

def get_DateString(m_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time))
    
###############################################
#### GET ONE RECORD
###############################################
def get_OneRecord(fp, code_filter = ''):
    list5min = []
    code = get_String12(fp)
    if code == '':
        return 0, None, list5min
    name = ('%s' % struct.unpack("12s",fp.read(12))).decode('gbk')
    items = get_Long(fp)
    #print 'code:',code, 'name:',name, 'Items:',items, '...'
    if code_filter != '' and code_filter not in code:
        #print 'skip'
        fp.seek(items*(8*4), 1)
        return code, name, list5min
    # fp.seek(items*(8*4), 1)
    # return code, name, list5min
    for i in xrange(items):
        m_time = struct.unpack("L",fp.read(4))[0]
        m_fOpen = struct.unpack("f",fp.read(4))[0]
        m_fHigh = struct.unpack("f",fp.read(4))[0]
        m_fLow = struct.unpack("f",fp.read(4))[0]
        m_fClose = struct.unpack("f",fp.read(4))[0]
        m_fVolume = struct.unpack("f",fp.read(4))[0]
        m_fAmount = struct.unpack("f",fp.read(4))[0]
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
        
    #print 'done!'
    return code, name, list5min
    
def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num    

def GetStockInfo_fromFile(reader, check_code):
    # name = name.replace('(','').replace(')','').replace(':','').lower()
    check_code = check_code[2:]
    for one in reader:
        # print one, code
        code, name, info = one
        # print code,check_code
        if code == check_code:
            return info
    return 'N/A'
    
def GetSpurtList_OneDay(filename, code_filter = '', show_detail = True):
    list_result = []
    print 'Reading ', filename
    if not os.path.exists(filename):
        print 'Open file', filename, 'failed.'
        return
    fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    print 'Header *** flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    num = 0
    while True:
        code, name, lists = get_OneRecord(fp, code_filter)
        if code == 0:
            break
        if len(lists) > 0 and show_detail:
            print 'Got', code, name, len(lists)
        for line in lists:
            m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
            list_result.append([code[:8], m_fOpen, m_fHigh, m_fLow, m_fClose])
            if show_detail:
                print get_DateString(m_time),'   ', m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
        num += 1
    print 'Total', num
    return list_result
      
def GetSpurtList_recentdays(days=7):
    listtoday = []
    listyesterday = []
    listout = []
    for i in range(0, days):
        timestamp = time.localtime(time.time()-3600*24*i)
        timestr = time.strftime('%Y%m%d', timestamp)
        filename = 'input_qda/Quote'+timestr+'.qda'
        if os.path.exists(filename):
            print filename
            if listtoday == []:
                listtoday = GetSpurtList_OneDay(filename, '', False)
            else:
                listyesterday = GetSpurtList_OneDay(filename, '', False)
        else:
            print 'Skip', filename
        if listyesterday != []:
            break
        # getQDAfile(filename)
    # print listspurt
    lastclose = 0
    for one in listtoday:
        code, m_fOpen, m_fHigh, m_fLow, m_fClose = one
        if 'SH900' in code or 'SZ200' in code or 'SZ1' in code:
            continue
        first_or_default = next((x for x in listyesterday if x[0]==code), None)
        if first_or_default == None:
            continue
        lastclose = first_or_default[4]
        if ((m_fOpen - lastclose)*100/lastclose) < 5 and ((m_fClose - lastclose)*100/lastclose) > 9.5:
            value_str = GetStockInfo_fromFile(csv.reader(file('stockinfo_cn.csv','rb')), code)
            listout.append(['cn', code, round(((m_fOpen - lastclose)*100/lastclose), 2), value_str])
    save2csv('cn_spurt_today.csv', listout)
     
     
########################################################################
if __name__ == '__main__':
    # getQDAfile()
    GetSpurtList_recentdays(7)
    
    