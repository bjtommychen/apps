import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import struct
import argparse

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
# sys.setdefaultencoding('utf8')
sys.setdefaultencoding('gbk')

data_path = 'input_qda/'
data_ext = 'qda'
# listfile_sh = 'sh_list.csv'
# listfile_sz = 'sz_list.csv'
output_path = 'output/'
bUseMultiCore = False
thread_num=8

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
    return str(time.strftime('%Y/%m/%d', time.gmtime(m_time)))

def get_TimeFromString(time_string):
    return time.mktime(time.strptime(time_string, '%Y/%m/%d'))-time.timezone   
    
def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num    
    
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

def write_QM_data_to_csv(filename, code, name, listall):
    print 'write_QM_data_to_csv', filename
    fcsv = open(filename, 'wb')
    csvWriter = csv.writer(fcsv)
    infoline = code, name, len(listall)
    csvWriter.writerow(infoline)
    for line in listall:
#        print line
# code, name, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull)
#         fp.write(struct.pack("LffffLLL",line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7]))
        m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
        if True:
            m_fOpen = float('%.2f' % m_fOpen)
            m_fHigh = float('%.2f' % m_fHigh)
            m_fLow = float('%.2f' % m_fLow)
            m_fClose = float('%.2f' % m_fClose)
        wline = get_DateString(m_time), m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
#         print m_time
        csvWriter.writerow(wline)
    fcsv.close()        
    
def get_AllQMdata():
    reader = csv.reader(file(listfile_sh,'rb'))    
    i = 0
    pool = workerpool.WorkerPool(size=thread_num, maxjobs=thread_num)
    for row in reader:
        print row
        Get_OneQMData(pool, data_path,data_ext, row[0].upper(), row[1])

    reader = csv.reader(file(listfile_sz,'rb'))  
    for row in reader:
        print row
        Get_OneQMData(pool, data_path,data_ext, row[0].upper(), row[1])

    pool.shutdown()
    pool.wait()
    
def get_NextRecord(fp, code_filter = ''):
    if True:
        code = get_String12(fp)
        if code == '':
            return '', '', []
        name = '%s' % struct.unpack("12s",fp.read(12))
        items = struct.unpack("L",fp.read(4))[0]
#         print code, name, items
        # if code_filter != '' and code_filter not in code:
            # fp.seek(items*(8*4), 1)
            # continue
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
    return '', '', []    
    
def update_QDA_to_csv(filename, code, name, listall):
    if not os.path.exists(filename):
        print 'write_QDA_data_to_csv', filename, len(listall)
        fcsv = open(filename, 'wb')
        csvWriter = csv.writer(fcsv)
        title = 'Date' ,'Open','High','Low','Close','Volume','Adj Close'
        csvWriter.writerow(title)
        for line in listall:
            m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
            if True:
                m_fOpen = float('%.2f' % m_fOpen)
                m_fHigh = float('%.2f' % m_fHigh)
                m_fLow = float('%.2f' % m_fLow)
                m_fClose = float('%.2f' % m_fClose)
            wline = get_DateString(m_time), m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
            csvWriter.writerow(wline)
        fcsv.close()            
    else:
        reader = csv.reader(file(filename,'rb'))
        list_old = []
        for one in reader:
            list_old.append(one)
        # print list_old[1]
        # print get_TimeFromString(list_old[1][0])
        # print listall[len(listall)-1]
        if listall[len(listall)-1][0] > get_TimeFromString(list_old[1][0]):
            print 'update_QDA_data_to_csv', filename, len(listall)
            fcsv = open(filename, 'wb')
            csvWriter = csv.writer(fcsv)            
            csvWriter.writerow(list_old[0])
            for line in listall:
                m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = line
                if True:
                    m_fOpen = float('%.2f' % m_fOpen)
                    m_fHigh = float('%.2f' % m_fHigh)
                    m_fLow = float('%.2f' % m_fLow)
                    m_fClose = float('%.2f' % m_fClose)
                wline = get_DateString(m_time), m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
                csvWriter.writerow(wline)
            for one in list_old[1:]:
                csvWriter.writerow(one)
            fcsv.close()  
    
    
def UpdateCSV_with_InputQDAfile(opath, filename):
    listall = []
    print filename  
    fp=open(filename,"rb")

    while(fp == 0):
        return
        # time.sleep(1)
        # print 'file open wait .............'
        # fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    while True:
        code, name, list_day = get_NextRecord(fp)
        if list_day != []:
            code = code.split('\x00')[0]
            name = name.split('\x00')[0]
            print code, name, len(list_day)
            list_day.sort(key=lambda data : data[0], reverse=True)
            update_QDA_to_csv(opath + code + '_qda.csv', code, name, list_day) 
            # break
        else:
            break
    fp.close()
    
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Convert/Update QDA data into csv format, one by one.'
    print '#'*60
    print 'Config:'

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store', dest='filename', default='input.qm1', help='Specify the QDA data file to read.')       
    parser.add_argument('-opath', action='store', dest='output_path', default='.\\output\\', help='Specify the output path to write/update.')       
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s v1.0')
    args = parser.parse_args()  
    
    print 'Start !'
    UpdateCSV_with_InputQDAfile(args.output_path, args.filename)
    print 'Completed !'
    