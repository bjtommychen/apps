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

data_path = 'qm1/'
data_ext = 'qm1'
listfile_sh = 'sh_list.csv'
listfile_sz = 'sz_list.csv'
output_path = 'output/'

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
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time)))


def get_OneRecordSpecified(fp, code_filter = ''):
    while True:
        code = get_String12(fp)
        if code == '':
            return '', '', []
        name = '%s' % struct.unpack("12s",fp.read(12))
        items = struct.unpack("L",fp.read(4))[0]
#         print code, name, items
        if code_filter != '' and code_filter not in code:
            fp.seek(items*(8*4), 1)
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
    return '', '', []

def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num    
    
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

def get_AllQMdata_for_one(datapath, ext, filter, sname):
    dirlist = getFileList(datapath, '*.'+ext, subdir = False)
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
    code = filter
    if len(listall) > 100:
        write_QM_data(output_path + filter + '.' + ext, code, sname, listall)
        write_QM_data_to_csv(output_path + filter + '_' +ext +'.' + 'csv', code, sname, listall)


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
    for row in reader:
        print row
        get_AllQMdata_for_one(data_path,data_ext, row[0].upper(), row[1])
#         get_AllQMdata_for_one('qm5/','qm5', row[0].upper())
#         if i==0:
#             break

    reader = csv.reader(file(listfile_sz,'rb'))  
    for row in reader:
        print row
        get_AllQMdata_for_one(data_path,data_ext, row[0].upper(), row[1])
#        get_AllQMdata_for_one('qm5/','qm5', row[0].upper())
#         if i==0:
#             break
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Convert all qm1 data into csv format, one by one.'
    print '#'*60
    print 'Config:'
    print '\tdata_path =', data_path
    print '\tdata_ext =', data_ext
    print '\tlistfile_sh =', listfile_sh
    print '\tlistfile_sz =', listfile_sz
    print '\toutput_path =', output_path
    if len(sys.argv) > 1:
        exit(0)
    print '\n\nWait 5s to start ... Ctrl+C to cancle now !\n'
    time.sleep(5)
    
    print 'Start !'
#     get_AllQMdata_for_one('qm5/','qm5', 'SH600036')
    get_AllQMdata()
    print 'Completed !'
    