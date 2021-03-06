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

def QM5_parserAll(filename, code_filter, show_detail):
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
        if len(lists) > 0:
            print 'Got', code, name, len(lists)
        for line in lists:
            if show_detail:
                m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
                print get_DateString(m_time),'   ', m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
        num += 1
    print num  

#������  
if  __name__ == '__main__':
    print '#'*60
    print '##### List data from QM1 Data file. ���԰�'
    print '#'*60
    print 'Config:'


    parser = argparse.ArgumentParser()
    #parser.add_argument('-t', action='store', dest='taskid', default='-1', help='Specify the task id.')
    parser.add_argument('--filter', action='store', dest='filter', default='', help='Specify the filter, for example SH600036.')       
    parser.add_argument('-i', action='store', dest='filename', default='input.qm1', help='Specify the QM1/QM5 data file to read.')       
    parser.add_argument('--show_detail', action='store_true', dest='detail',default=False,help='print minute data.') 
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s v1.0')
    args = parser.parse_args()

    QM5_parserAll(args.filename, args.filter, args.detail)
    
    print 'Completed !'    