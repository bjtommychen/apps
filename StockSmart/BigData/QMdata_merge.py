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
#reload(sys) 
#sys.setdefaultencoding('utf8')
#sys.setdefaultencoding('gbk')

data_path = 'qm1_88158cn/'
data_ext = 'qm1'
listfile_sh = 'sh_list.csv'
listfile_sz = 'sz_list.csv'
output_path = 'output_tmp/'

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
        
def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num   
        
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
        
        
def get_AllQMdata_for_one(filter = 'SH600036'):
    #skip if already created.
    if os.path.exists(output_path+filter+'.'+data_ext):
        print 'skip'
        return
    dirlist = getFileList(data_path, '*.'+data_ext, subdir = True)
    listall = []
    code_write =''
    name_write =''
    for filename in dirlist:
        print filename  
        fp=open(filename,"rb")
        flag, version, total_num = get_QM_header(fp)
        print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
        code, name, list5min = get_OneRecordSpecified(fp, filter)
        print code, name, len(list5min)
        if len(list5min):
            listall += list5min
            code_write = code
            name_write = name
        fp.close()
    print 'Total', len(listall)
    if len(listall):
        print 'start sorting ... '
        listall.sort(key=lambda data : data[0], reverse=False)
        print 'sorted.'
        write_QM_data(output_path+filter+'.'+data_ext, code_write, name_write, listall)

def Get_AllQMdata_for_AllInList():    
    reader = csv.reader(file(listfile_sh,'rb'))    
    i = 0
    for row in reader:
        print row[0].upper()
        get_AllQMdata_for_one(row[0].upper())
        #get_AllQMdata_for_one('SH600086')

def MergeAll_AddOne(fp, filter):
    #skip if already created.
    filename = output_path+filter+'.'+data_ext
    if not os.path.exists(filename):
        print 'Not exit', filename
        return

    fp1=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp1)
    print 'Header *** flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    code = get_String12(fp1)
    name = ('%s' % struct.unpack("12s",fp1.read(12))) #.decode('gbk')
    items = get_Long(fp1)
    print 'code:',code, 'name:',name, 'Items:',items
    
    fp.write(struct.pack("12s",code))
    fp.write(struct.pack("12s",name))
    fp.write(struct.pack("L",items))    
    fp.write(fp1.read(items*(8*4)))
    fp1.close()
    
def MergeAllQMdata(filename):
    print 'writing QM_data', filename
    fp=open(filename,"wb")
    flag = 0xffffffe1
    version = 0x19730101
    total_num = 0xdeef
    fp.write(struct.pack("L",flag))
    fp.write(struct.pack("L",version))
    fp.write(struct.pack("L", 1))

    i = 0
    reader = csv.reader(file(listfile_sh,'rb'))    
    for row in reader:
        i += 1
        #if i > 3:
        #    break
        print row[0].upper()
        MergeAll_AddOne(fp, row[0].upper())
    fp.close()          
        
if  __name__ == '__main__':
    print '#'*60
    print '##### Merge QM1 data for code in list. ≤‚ ‘∞Ê' 
    print '#'*60
    print 'Config:'
    print '\tdata_path =', data_path
    print '\tdata_ext =', data_ext
    print '\tlistfile_sh =', listfile_sh
    print '\tlistfile_sz =', listfile_sz
    print '\toutput_path =', output_path
    print ''
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--filter', action='store', dest='filter', default='', help='Specify the filter, for example SH600036.')       
    parser.add_argument('-i', action='store', dest='filename', default='input.qm1', help='Specify the QM1/QM5 data file to read.')       
    parser.add_argument('--show_detail', action='store_true', dest='detail',default=False,help='print minute data.') 
    parser.add_argument('--debug', action='store_const', dest='debug',default=0,const=1,help='enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s v1.0')
    args = parser.parse_args()
    
    Get_AllQMdata_for_AllInList()
    MergeAllQMdata(output_path+'MergeAll.qm')
    