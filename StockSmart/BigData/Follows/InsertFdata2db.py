import os
import stat,fnmatch
import time
import sys
import stat,fnmatch
import pymysql
import csv
import struct

reload(sys) 
sys.setdefaultencoding('utf')

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
# hostip = '127.0.0.1'
conn = None
cur = None
def mysql_connect(hostip='localhost'):
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
    
    
def Insert_oneFdata2db(filename):
    global conn,cur
    ErrorCnt = 0
    sql_insert_prefix = "INSERT INTO `gp`.`gpf` (`idx`,`market`, `code`, `name`,`date`, `f`) VALUES"
    print filename.center(79, '-')
    if not os.path.exists(filename):
        print 'Not exist!', filename
        return False
    fp=open(filename,"rb")
    while(fp == 0):
        return

    if 'stock_follows-' in filename:
        market = 'cn'
        idx = filename.find('stock_follows-')+len('stock_follows-')
        datestr = filename[idx:idx+10]
    elif 'hk-' in filename:
        market = 'hk'
        idx = filename.find('hk-')+len('hk-')
        datestr = filename[idx:idx+10]
    elif 'nasdaq-' in filename:
        market = 'us'
        idx = filename.find('nasdaq-')+len('nasdaq-')
        datestr = filename[idx:idx+10]
        
    cnt = 0
    lista = loadfromecsv(filename)
    for one in lista:
        cnt += 1
        if cnt == 1:
            continue
        if ErrorCnt>100:
            break

        name, code, fdata = one
        name = name.strip()
        if cnt%1000==0:
            print '..',cnt,'..',
        if market == 'cn':
            code = code.replace('(','').replace(')','').replace(':','').upper()
        elif market == 'hk':
            code = code[code.find(':'):].replace('(','').replace(')','').replace(':','').upper()
        elif market == 'us':
            code = code[code.find(':')+1:].replace('(','').replace(')','').upper()  
        one_row = str((code+'-'+datestr , market, code, 'goodwill', datestr, int(fdata)))
        one_row = one_row.replace('goodwill', name.decode('gbk'))
        sqlcmd = sql_insert_prefix + one_row    
        try:
            # print sqlcmd
            # break
            cur.execute(sqlcmd)
        except Exception, e:
            # print Exception, e
            ErrorCnt += 1
            pass            
    conn.commit()
    print ''
    if ErrorCnt < 100:
        return True
    else:
        print 'Too many Error, exit.'
        return False

def Insert_onecsv2db_all_fdata():
    filelist = getFileList('.\\data\\', '*.csv')
    for one in filelist:
        # print one
        # if not 'nasdaq-' in one:
            # continue
        Insert_oneFdata2db(one)
        # break

def Insert_fdata2db_recentdays(days=10):
    for i in range(0, days):
        timestamp = time.localtime(time.time()-3600*24*i)
        timestr = time.strftime('%Y-%m-%d', timestamp)
        filelist = getFileList('.\\data\\', '*'+timestr+'*.csv')
        for one in filelist:
            # print one
            Insert_oneFdata2db(one)
        
########################################################################
if __name__ == '__main__':
    print 'Start ... '
    print (' Processing Mysql').center(79, '-')
    mysql_connect('localhost')
    # Insert_onecsv2db_all_fdata()
    Insert_fdata2db_recentdays()
    mysql_disconnect()
    print 'End!'