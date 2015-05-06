import sys
import pymysql
import time
import subprocess
import multiprocessing

conn = None
cur = None
debug_mysql = True

def mysql_setdebug(mode = True):
    global debug_mysql
    debug_mysql = mode

def mysql_connect(hostip='localhost'):
    global conn,cur
    try:
        conn = pymysql.connect(host=hostip, user='tommy', db='gp', charset='utf8')
    except:
        print 'sql connect failed !'
        return False
    cur = conn.cursor()
#     print 'Description', cur.description
    cur.execute("SELECT VERSION()")
    print cur.fetchall()
    return True

def mysql_execute(sqlcmd):
    global conn,cur
    global debug_mysql
    if debug_mysql:
        print sqlcmd
    cur.execute(sqlcmd)
    # fetchone()
#     print 'Description', cur.description
    return cur.fetchall()
    
def mysql_getDescription():
    global conn,cur
    return cur.description
    
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

# SELECT *FROM `gpday` WHERE `code` LIKE 'sh600036' AND `date` > '2015-04-08' 
# SELECT *FROM `gpday` WHERE `code` LIKE 'SH600036' AND `date` BETWEEN '2015-04-16' AND '2015-04-30' 
def mysql_GetDayByCodeDate(code = 'sh600036', datestart='', dateend=''):
    cmd1 = "SELECT date_format(date, '%%Y-%%m-%%d'),open,high,low,close,volume,amount FROM `gpday` WHERE `code` LIKE \'%s\' ORDER BY `date` ASC "
    cmd2 = "SELECT date_format(date, '%%Y-%%m-%%d'),open,high,low,close,volume,amount FROM `gpday` WHERE `code` LIKE \'%s\' AND `date` > \'%s\' ORDER BY `date` ASC "
    cmd3 = "SELECT date_format(date, '%%Y-%%m-%%d'),open,high,low,close,volume,amount FROM `gpday` WHERE `code` LIKE \'%s\' AND `date` BETWEEN \'%s\' AND \'%s\' ORDER BY `date` ASC "
    if datestart == '' and dateend == '':
        cmd_run = cmd1 % code
    elif datestart != '' and dateend == '':
        cmd_run = cmd2 %(code, datestart)
    else:
         cmd_run = cmd3 %(code, datestart, dateend)
    # print cmd_run
    listall = mysql_execute(cmd_run)
    return listall
    
    
def mysql_GetDayByIdx(idx = '%'):
    cmd1 = "SELECT date_format(date, '%%Y-%%m-%%d'),open,high,low,close,volume,amount FROM `gpday` WHERE `idx` like \'%s\' ORDER BY `date` ASC "
    cmd_run = cmd1 % idx
    # print cmd_run
    listall = mysql_execute(cmd_run)
    return listall    
    
    
def mysql_Get1MinByCodeDate(code = 'sh600036', datestart='', dateend=''):
    cmd1 = "SELECT date_format(datetime, '%%Y-%%m-%%d %%H:%%i'),open,high,low,close,volume,amount FROM `gp1min` WHERE `code` LIKE \'%s\' ORDER BY `datetime` ASC "
    cmd2 = "SELECT date_format(datetime, '%%Y-%%m-%%d %%H:%%i'),open,high,low,close,volume,amount FROM `gp1min` WHERE `code` LIKE \'%s\' AND `datetime` > \'%s\' ORDER BY `datetime` ASC "
    cmd3 = "SELECT date_format(datetime, '%%Y-%%m-%%d %%H:%%i'),open,high,low,close,volume,amount FROM `gp1min` WHERE `code` LIKE \'%s\' AND `datetime` BETWEEN \'%s\' AND \'%s\' ORDER BY `datetime` ASC "
    if datestart == '' and dateend == '':
        cmd_run = cmd1 % code
    elif datestart != '' and dateend == '':
        cmd_run = cmd2 %(code, datestart)
    else:
         cmd_run = cmd3 %(code, datestart, dateend)
    # print cmd_run
    listall = mysql_execute(cmd_run)
    return listall    
    
def mysql_Get1MinByIdx(idx = '%'):
    cmd1 = "SELECT date_format(datetime, '%%Y-%%m-%%d %%H:%%i'),open,high,low,close,volume,amount FROM `gp1min` WHERE `idx` like \'%s\' ORDER BY `datetime` ASC "
    cmd_run = cmd1 % idx
    # print cmd_run
    listall = mysql_execute(cmd_run)
    return listall  

def show_list(lista):
    for one in lista:
        print one

def mysql_GetStockList(market = 'cn'):
    cmd_run = "SELECT code,name,volume  FROM `stockinfo` WHERE `market` LIKE \'%s\'" % market
    # print cmd_run
    listall = mysql_execute(cmd_run)
    return listall    
    
####
def show_list(lista):
    for one in lista:
        print one
        
def GetVol1min_avg(code='SH600036', timestr='0931'):
    cmd1 = "SELECT count(volume),avg(volume) FROM `gp1min` WHERE `idx` LIKE \'%s-%%%s\' and TIMESTAMPDIFF(day,datetime,now()) < 10"
    cmd_run = cmd1 % (code, timestr)
    listout = list(mysql_execute(cmd_run))
#     print timestr, len(listout[0])
    return listout[0]
    
def get_stock_timemin():
    list_min = []
    timetext = time.strftime("%Y-%m-%d", time.localtime())
#     print timetext
    time_string = timetext + ' 09:30'
    time_start = time.mktime(time.strptime(time_string, '%Y-%m-%d %H:%M'))-time.timezone
#     print time_start
    time_end = time_start + 5.5*3600
    time_m = time_start
    while time_m <= time_end:
        if time_m > (time_start + 3600*2) and time_m < (time_start + 3600*3.5):
            time_m += 60
            continue
        strout = time.strftime("%H%M", time.gmtime(time_m))
        list_min.append(strout)
        time_m += 60
#     print list_min 
    return list_min
    
list_min = []    
def GetVol1min_byCodeTime(code='SH600036'):
    global list_min
    listout = []
    total = 0
    for onemin in list_min:
#         print onemin,
        cnt, volavg = GetVol1min_avg(code, onemin)
        if cnt == 0:
            total = total
        else:
            total += int(volavg)
        listout.append([onemin,total])
    return listout        

def UpdateDB_byCodeTime(code='SH600036'):
    global conn,cur
    listout = GetVol1min_byCodeTime(code)
    print 'len', len(listout)
    current_timetext = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    ErrorCnt = 0
    for one in listout:
        timestr, volume = one
        cmd1="INSERT INTO vol1min (idx,code,time,volume,updatetime) VALUES(\'%s\',\'%s\',\'%s\',%d, \'%s\') ON DUPLICATE KEY UPDATE volume = %d, updatetime = \'%s\'"
        sqlcmd = cmd1 %(code+'-'+timestr, code, timestr, volume, current_timetext, volume, current_timetext)
        try:
#             print sqlcmd
            # break
            cur.execute(sqlcmd)
        except Exception, e:
            # print Exception, e
            ErrorCnt += 1        
    conn.commit()
    
def InsertDB_byCodeTime(code='SH600036'):
    global conn,cur
    listout = GetVol1min_byCodeTime(code)
    print 'len', len(listout)
    current_timetext = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    ErrorCnt = 0
    sqlcmd = "INSERT INTO vol1min (idx,code,time,volume,updatetime) VALUES "
    i = 0
    for one in listout:
        if i != 0:
            sqlcmd += ','
        i += 1        
        timestr, volume = one
        cmd1="(\'%s\',\'%s\',\'%s\',%d, \'%s\')"
        one_row = cmd1 %(code+'-'+timestr, code, timestr+'00', volume, current_timetext)
        sqlcmd += one_row
    try:
        # print sqlcmd
        # break
        cur.execute(sqlcmd)
    except Exception, e:
        # print Exception, e
        ErrorCnt += 1
    # print 'conn', conn, cur
    conn.commit()    

def InsertDB_byCodeTime_MP(code='SH600036'):
    conn = pymysql.connect(host='192.168.99.9', user='tommy', db='gp', charset='utf8')
    cur = conn.cursor()
    print conn, cur
    listout = GetVol1min_byCodeTime(code)
    print 'len', len(listout)
    current_timetext = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    ErrorCnt = 0
    sqlcmd = "INSERT INTO vol1min (idx,code,time,volume,updatetime) VALUES "
    i = 0
    for one in listout:
        if i != 0:
            sqlcmd += ','
        i += 1        
        timestr, volume = one
        cmd1="(\'%s\',\'%s\',\'%s\',%d, \'%s\')"
        one_row = cmd1 %(code+'-'+timestr, code, timestr+'00', volume, current_timetext)
        sqlcmd += one_row
    try:
        # print sqlcmd
        # break
        cur.execute(sqlcmd)
    except Exception, e:
        # print Exception, e
        ErrorCnt += 1
    # print 'conn', conn, cur
    conn.commit()    
    cur.close()
    conn.close()
    
def UpdateVol1min_All():
    stocklist = mysql_GetStockList()
#     print stocklist[:5]
    cnt = 0
    length = len(stocklist)
    for one in stocklist:
        code, name, volume = one
        print '.',cnt,'/',length,code,'.'
        InsertDB_byCodeTime(code)
        cnt += 1

MAX_PROCESSING = 1
def run_cmdline_processing(q, lock, code):
    print 'run_cmdline_processing', code
    lock.acquire()
    try:
        InsertDB_byCodeTime_MP(code)
    except Exception, e:
        print 'error', Exception, e
    lock.release()            
        
def UpdateVol1min_All_multiprocessing():
    global list_min
    stocklist = mysql_GetStockList()

    p_list = []
    print 'multiprocessing.cpu_count()', multiprocessing.cpu_count()
    q = multiprocessing.Queue()
    q.put([])
    lock = multiprocessing.Lock()
    cnt = 0
    for one in stocklist:
        cnt += 1
        code, name, volume = one
        # print '.',cnt,'/',length,code,'.'        
        print (' Processing No.'+str(cnt)+'/'+str(len(stocklist))+code).center(79, '-')
        # print line
        p = multiprocessing.Process(target=run_cmdline_processing, args=(q, lock, code))
        p.start()
        p_list.append(p)
        # print p,'added'
        time.sleep(0.2)
        while(len(p_list) >= MAX_PROCESSING):
            print 'Waiting ...'
            time.sleep(1)
            for p in p_list:
                # print p
                p.join(timeout=0.1)
                if not p.is_alive():
                    p_list.remove(p)
                    # handle_ResultsInQueue(q.get())
                    # print 'Removing Process', p
    for p in p_list:
        # print 'wait join', p
        p.join()
        # handle_ResultsInQueue(q.get())
    result_logs = q.get()
    
    print 'result_logs', len(result_logs), result_logs
    print 'All Done!'   
        
########################################################################
if __name__ == '__main__':
    print 'Start ... '
    print (' Processing Mysql').center(79, '-')
    if list_min == []:
        list_min = get_stock_timemin()    
    
    mysql_setdebug(False)
    if not mysql_connect('192.168.99.9'):
        sys.exit(1)  
#     mysql_GetDayByIdx('SH600036-20150101')
    print mysql_getDescription()
    
    print "TRUNCATE TABLE `vol1min`"
    mysql_execute("TRUNCATE TABLE `vol1min`")
#     show_list(GetVol1min_avg())
#     UpdateDB_byCodeTime()
    start = time.time()
    UpdateVol1min_All()
    end = time.time()
    print 'time last',end-start
    # UpdateVol1min_All_multiprocessing()
    # InsertDB_byCodeTime()
#     print listout, len(listout)
    mysql_disconnect()
    print 'End!'    