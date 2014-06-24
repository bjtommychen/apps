# -*- coding: utf-8 -*
import time
import sys
import os
import math
import csv
import stat,fnmatch
import struct
import argparse  

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')
#sys.setdefaultencoding('gbk')

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
    
def get_TimeFromString(time_string):
    return time.mktime(time.strptime(time_string, '%Y-%m-%d %H:%M:%S'))-time.timezone
    
###############################################
#### GET ONE RECORD
###############################################
def get_OneRecord_by(fp, code_filter = ''):
    list5min = []
    code = get_String12(fp)
    code = code[:8]
    #print code
    if code == '':
        return 0, None, list5min
    name = ('%s' % struct.unpack("12s",fp.read(12))).decode('gbk')
    items = get_Long(fp)
    #print 'code:',code, 'name:',name, 'Items:',items, '...'
    if code_filter != '' and code not in code_filter:
        #print 'skip'
        fp.seek(items*(8*4), 1)
        return code, name, list5min
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
    #print 'done!'
    return code, name, list5min
    
def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num    


    
def QM5_GetListByDate(filename, code_lists, time_string):    
    #print 'Reading ', filename, 'for lists:', code_lists
    if not os.path.exists(filename):
        print 'Open file', filename, 'failed.'
        return
    fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    #print 'Header *** flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    num = 0
    ret_lists = []
    check_time = get_TimeFromString(time_string)
    while True:
        code, name, lists = get_OneRecord_by(fp, code_lists)
        if code == 0:
            break
        #if len(lists) > 0:
        #    print 'Got', code, name, len(lists), type(code)            
        if len(lists) > 0 and code in code_lists:
            #print 'found', code, name, len(lists)
            #print type(check_time), check_time
            for line in lists:
                m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
                #print type(m_time), m_time
                if check_time == m_time:
                    #print get_DateString(m_time),'   ', m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
                    ret_lists.append((code, name, line))
        num += 1
    return ret_lists

    
#Ö÷º¯Êý  
if  __name__ == '__main__':
    print '#'*60
    print '##### Get data from QM1 Data file. ²âÊÔ°æ'
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

    #QM5_parserAll(args.filename, args.filter, args.detail)
    
    code_lists = ['SH600036', 'SH601857', 'SH603993']
    r=QM5_GetListByDate(args.filename, code_lists, '2014-03-03 09:31:00')
    print r
    r=QM5_GetListByDate(args.filename, code_lists, '2014-03-03 09:35:00')
    print r
    
    print 'Completed !'    