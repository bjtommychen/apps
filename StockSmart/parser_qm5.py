import sys
import os
import struct
import csv
import stat,fnmatch
import profile
import time

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
#sys.setdefaultencoding('utf8')
#sys.setdefaultencoding('ascii')

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

###############################################
#### GET ONE RECORD
###############################################
def get_OneRecordSpecified(fp, code_filter = ''):
    while True:
        code = get_String12(fp)
        if code == '':
            return 0, 0, []
        name = '%s' % struct.unpack("12s",fp.read(12))
        items = struct.unpack("L",fp.read(4))[0]
        print code, name, items
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
            print line
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

def QM5_parserOne(filename, code_filter = ''):
    fp=open(filename,"rb")
    flag, version, total_num = get_QM_header(fp)
    print '0x%08x' % flag, '0x%08x' % version, '0x%08x' % total_num
    
    code, name, list5min = get_OneRecordSpecified(fp, 'SH600036')
    print code, name, len(list5min)
    print list5min
    
    
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

def get_AllQMdata_for_one(ext, filter):
    dirlist = getFileList('qm5_data/', '*.qm1', subdir = False)
    listall = []
    for filename in dirlist:
        print filename  
        fp=open(filename,"rb")
        flag, version, total_num = get_QM_header(fp)
        code, name, list5min = get_OneRecordSpecified(fp, 'SH600036')
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
    QM5_parserAll(filename)


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
if  __name__ == '__main__':
    
    start = time.time()
    print 'start!'
#    QM5_parser('Quote.QM5')
#    QM5_parser('qm5_data/5F201307.QM5')
#    QM5_parserOne('qm5_data/201307.QM1')
#    QM5_parserOne('qm5_data/201307.QM1')
    QM5_parserAll('test.qm5')

#     get_AllQMdata_for_one('*.qm5', 'SH600036')
    print 'done!'
    end = time.time()
    elapsed = end - start
    print "Time taken: ", elapsed, "seconds."
    