import sys
import pymysql

reload(sys) 
sys.setdefaultencoding('utf')

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
   
########################################################################
if __name__ == '__main__':
    print 'Start ... '
    print (' Processing Mysql').center(79, '-')
    
    if not mysql_connect('localhost'):
        sys.exit(1)  
    mysql_GetDayByIdx('SH600036-20150101')
    print mysql_getDescription()

    listall = mysql_GetDayByCodeDate('sh600036', '2015-01-11', '2015-04-15')
    print 'listall, len:',len(listall)
    listall = mysql_GetDayByIdx('SH600036-2015%')
    print 'listall, len:',len(listall), listall[0]
    
    listall = mysql_Get1MinByIdx('SH600036-2015%')
    print 'listall, len:',len(listall)    
    listall = mysql_Get1MinByCodeDate('sh600036', '2015-01-01', '2015-12-31')
    print 'listall, len:',len(listall), listall[0] 
    
    listall = mysql_GetStockList()
    print 'cn list', len(listall)
    listall = mysql_GetStockList('hk')
    print 'hk list', len(listall)
    listall = mysql_GetStockList('us')
    print 'us list', len(listall)

    print mysql_execute("SELECT * FROM `gpf` WHERE `idx` LIKE 'cyou%' ORDER BY `idx` DESC")[0:5]
    mysql_disconnect()
    print 'End!'