import os
import stat,fnmatch
import time
import sys
import stat,fnmatch
import pymysql
import csv
import struct

def save2csv(fname, list):
    fcsv = open(fname, 'wb')
    csvWriter = csv.writer(fcsv)
    csvWriter.writerows(list)
    fcsv.close()
        
def loadfromecsv(fname):
    lista = []
    reader = csv.reader(file(fname,'rb'))
    for line in reader:        
        lista.append(line)
    return lista

####### mysql #########
# hostip = '10.10.32.29'
hostip = '127.0.0.1'
conn = None
cur = None
def mysql_connect():
    global conn,cur
    conn = pymysql.connect(host=hostip, user='tommy', db='gp', charset='utf8')
    cur = conn.cursor()
    print 'Description', cur.description
    cur.execute("SELECT VERSION()")
    print cur.fetchall()
    
def mysql_execute(sqlcmd):
    global conn,cur
    cur.execute(sqlcmd)
    return cur.fetchall()
    
def mysql_insert(sqlcmd):
    global conn,cur
    try:
        cur.execute(sqlcmd)
        conn.commit()
        return True
    except:
        return False
    
def mysql_disconnect():    
    global conn,cur
    cur.close()
    conn.close()

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
    return str(time.strftime('%Y-%m-%d', time.gmtime(m_time)))

def get_TimeFromString(time_string):
    return time.mktime(time.strptime(time_string, '%Y-%m-%d'))-time.timezone   
    
def get_QM_header(fp):
    flag = get_Long(fp)
    version = get_Long(fp)
    total_num = get_Long(fp)
    return flag, version, total_num     
    
    
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
            m_fVolume = struct.unpack("f",fp.read(4))[0]
            m_fAmount = struct.unpack("f",fp.read(4))[0]
            m_fNull = struct.unpack("L",fp.read(4))[0]
    #        print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time))
            line = (m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull)
#             print line
            list5min.append(line) 
        return code, name, list5min
    return '', '', []    
    
def Insert_onecsv2db_gpday(filename):
    global conn,cur
#     filename = 'd:\\workspace\\apps\\StockSmart\\BigData\\Follows\\qda_all\\Quote20150422.QDA'
#     str_insert = "INSERT INTO `gp`.`gpday` (`idx`, `code`, `date`, `open`, `high`, `low`, `close`, `volume`, `amount`) \
#     VALUES ('sh_webphon', 'code15', '1973-01-01', '1.1', '5.55', '135.5', '35000', '135', '15');"
    sql_insert_prefix = "INSERT INTO `gp`.`gpday` (`idx`, `code`, `name`,`date`, `open`, `high`, `low`, `close`, `volume`, `amount`) VALUES"
#     sql_insert_prefix = "INSERT INTO `gp`.`test` (`name`) VALUES"
    print filename.center(79, '-')
    fp=open(filename,"rb")

    while(fp == 0):
        return
    flag, version, total_num = get_QM_header(fp)
    print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    cnt = 0
    while True:
        code, name, list_day = get_NextRecord(fp)
        if list_day != []:
            code = code.split('\x00')[0]
            name = name.split('\x00')[0]
            cnt += 1
            if cnt%100==0:
                print '..',cnt,'..',
            if True:
                # print code, name.decode('gbk'), len(list_day)
                for one in list_day:
                    m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = one
                    datestr = str(time.strftime('%Y%m%d', time.gmtime(m_time)))
                    one_row = str((code+'-'+datestr, code, 'goodwill', datestr, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount))
                    one_row = one_row.replace('goodwill', name.decode('gbk'))
#                     print one_row
                    sqlcmd = sql_insert_prefix + one_row #'(\''+ () +'\');'
                    try:
                        # print sqlcmd
                        cur.execute(sqlcmd)
                    except:
                        pass
#                     conn.commit()
#                 break
            conn.commit()
        else:
            break
    print ''
    fp.close()       
    
def Insert_onecsv2db_gp1min(filename):
    global conn,cur
    sql_insert_prefix = "INSERT INTO `gp`.`gp1min` (`idx`, `code`, `name`,`datetime`, `open`, `high`, `low`, `close`, `volume`, `amount`) VALUES"
    print filename.center(79, '-')
    fp=open(filename,"rb")

    while(fp == 0):
        return
    flag, version, total_num = get_QM_header(fp)
    print 'flag:0x%08x' % flag, 'version:0x%08x' % version, 'total_num:0x%08x' % total_num
    cnt = 0
    while True:
        code, name, list_day = get_NextRecord(fp)
        if list_day != []:
            code = code.split('\x00')[0]
            name = name.split('\x00')[0]
            cnt += 1
            if cnt%100==0:
                print '..',cnt,'..',
            if True:
                # print code, name.decode('gbk'), len(list_day)
                for one in list_day:
                    m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount, m_fNull = one
                    datestr = str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(m_time)))
                    datestr2 = str(time.strftime('%Y%m%d-%H%M', time.gmtime(m_time)))
                    one_row = str((code+'-'+datestr2, code, 'goodwill', datestr, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount))
                    one_row = one_row.replace('goodwill', name.decode('gbk'))
#                     print one_row
                    sqlcmd = sql_insert_prefix + one_row #'(\''+ () +'\');'
                    try:
                        # print sqlcmd
                        cur.execute(sqlcmd)
                    except:
                        pass
                    # conn.commit()
                # break
            conn.commit()
        else:
            break
    print ''
    fp.close()      
    
def Insert_onecsv2db_all_gpday():
    # filelist = getFileList('d:\\workspace\\apps\\StockSmart\\BigData\\Follows\\qda_all\\', '*.qda')
    filelist = getFileList('./input_qda/', '*.qda', False)
    for one in filelist:
        Insert_onecsv2db_gpday(one)
    
def Insert_onecsv2db_all_gp1min():
    filelist = getFileList('./input_qda1m/bak/', '*.qda', False)
    for one in filelist:
        Insert_onecsv2db_gp1min(one)
        # break
    
########################################################################
if __name__ == '__main__':
    print 'Start ... '
    print (' Processing Mysql').center(79, '-')
    mysql_connect()
#     Insert_onecsv2db('')
    # Insert_onecsv2db_all_gpday()
    Insert_onecsv2db_all_gp1min()
    mysql_disconnect()
    print 'End!'