
import time
import sys
import os
import socket
import math
import csv
import shutil
import random
import datetime

#import winsound

from StockSmart import *
from Gtalk_test import *
from mail_process import *

code_list = ['sh600036', 'sh601328']
buy_max = 0        

#windows: GBK
#ubuntu: ascii
print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')
#sys.setdefaultencoding('ascii')


def beep_sos(): 
    sys.stdout.write('\a')
#    for i in range(0, 3): 
#        winsound.Beep(2000, 100) 
#    for i in range(0, 3): 
#        winsound.Beep(2000, 400)
#    for i in range(0, 3):
#        winsound.Beep(2000, 100)

def autoreload():
    mod_names = ['Gtalk_test', 'StockSmart']
    for mod_name in mod_names:
        try:
            module = sys.modules[mod_name]
        except:
            continue
        mtime = os.path.getmtime(module.__file__)
        try:
            if mtime > module.loadtime:
                reload(module)
        except:
            pass
        module.loadtime = mtime


def test_StockSmart():
    test_google()
    test_sina()
    get_stockindex('s_sh000001')
    get_all_price(code_list)
    get_K_char('600036', '1m')

def check_market_open():
    checkopen = False
    if (datetime.datetime.now().weekday() > 4):
        return False
    text = time.strftime("%H:%M", time.localtime())
    if text > '09:20' and text <= '11:30':
        checkopen = True
    elif text >= '13:00' and text <= '15:00':
        checkopen = True
#    print text, checkopen,
    return checkopen

def check_market_justopen():
    checkopen = False
    text = time.strftime("%H:%M", time.localtime())
    if text == '09:30':
        checkopen = True
    elif text == '13:00':
        checkopen = True
    return checkopen

def check_if_need_send_analysis_report():
    checkopen = False
    if (datetime.datetime.now().weekday() > 4):
        return False    
    text = time.strftime("%H:%M", time.localtime())
    if not check_market_open():
        return False
    if ':30' in text or ':00' in text:
        checkopen = True
    return checkopen

def stock_daemon():
    '''Get the price of stock list, then send it out through Gtalk.
    
    No arguments. '''
    print 'enter stock_daemon.'
    price_old = 0.0
    inited = False
    market_open = False
    need_checkall = True
    DebugAll = False
    Gtalk_enable_send(True)
    Gtalk_send("stock_daemon v2.0 Online." + socket.gethostname())
    Gtalk_send("send 'stock help' for helps.")
    text = ''
    try:
        while True:
            index = 0
            diff = False
            
            if market_open != check_market_open():
                price_old = 0.
                market_open = check_market_open()
                
            if check_if_need_send_analysis_report() or DebugAll:
                if need_checkall or DebugAll:
                    Gtalk_send('Preparing analysis reoprt...')
                    maintext = check_all_open()
                    attach_filename = 'data/check_all_open_'+time.strftime("%Y-%m-%d_%H%M", time.localtime())+'.csv'
                    print attach_filename
                    shutil.copy2("check_all_open.csv", attach_filename)
                    send_mail("Notice: check_all_open.csv is Ready!", "Hi!\nCreate time:"+time.strftime("%Y-%m-%d_%H%M", time.localtime()) + maintext,
                               attach_filename)
                    need_checkall = False
                    Gtalk_send('Sent mail with check_all_open.csv, please check soon!')
            else:
                need_checkall = True
                
            text = ''
            #get time
            text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
            if not market_open:
                text += 'Close'
                need_checkall = True
            text += '\n'
            #get price
            for code in code_list:
                name, price_current, price_diff, change_percent = get_price(code)
                if price_current == 0.:
                    print 'get price failed!'
                    break
                if index == 0:
                    if price_old == 0.:
                        price_old = price_current
                        diff = True
                    if price_current != price_old:
                        diff_ppk = abs((price_current - price_old)*1000/price_old)
#                        print 'diff_ppk is', diff_ppk,
                        diff = diff_ppk > 2
                    if diff:
                        price_old = price_current
                text += '%s: %s, %s, %s%%' %(name,price_current, price_diff, change_percent)
                text += '\n'
                index += 1    
            if diff or DebugAll:
                Gtalk_send(text)
#            else:
#                print 'same ',
            sleep_seconds = 5
            DebugAll = False
            while(sleep_seconds):
                sleep_seconds = sleep_seconds - 1
                cmds = Gtalk_GetCustomCmd('stock')
#                print 'Gtalk_GetCustomCmd return', cmds
                if cmds and len(cmds.split(' ')) > 1:
#                    print 'Get Custom Cmds:', cmds
                    cust_cmds = cmds.split(' ')[1]
                    print 'Stock Custom commands:', cust_cmds
                    if (cust_cmds == 'help'):
                        Gtalk_send('Stock helps:\nstock guess: get check_all_open.csv by mail.')
                    elif (cust_cmds == 'guess'):
                        DebugAll = True
                    sleep_seconds = 0
                time.sleep(1)
#                print '.'
                
            if not Gtalk_isRunning():
                Gtalk_send("Gtalk sleep, wakeup it!")
            inited = True
    except KeyboardInterrupt:
        print 'Exception!'
    finally:
        Gtalk_exit()
        time.sleep(1)
     
#########################################################################
def get_percent(value, base):
    percent = (value - base) *100 / base
    return float('%.1f' % percent) 

def get_percent_str(value, base):
    percent = (float(value) - float(base)) *100. / float(base)
    return float('%.1f' % percent) 


def avg(sequence):
        if len(sequence) < 1:
            return None
        else:
            return round(sum(sequence) / len(sequence), 3)     

def FloatIsEqual(f1, f2):
    if (math.fabs(f1-f2)<1e-6): 
        return True
    else:
        return False
        
def get_price_map():
    code = '600036'
    mlen = '36m'
    k_list = get_K_array(code, mlen)        
    print k_list
    print len(k_list)
    print len(k_list[1])
    
    idx_date = 1;
    idx_close = 3;
    idx_high = 5;
    idx_low = 7;
    idx_open = 9;
    idx_volume = 11;
    
    f = open(code + '_' + mlen + '.txt', 'w')
    
    for i in range(1, len(k_list)):
        string = k_list[i][idx_date] + ', '
        string += str(get_percent( k_list[i][idx_open], k_list[i-1][idx_close])) + ', '
        string += str(get_percent(k_list[i][idx_high],k_list[i][idx_open])) + ', '
        string += str(get_percent(k_list[i][idx_low],k_list[i][idx_open]))
#        print string
#        f.write(string+'\n')
    
    for jj in range(-30, 30, 1):
        j = jj/10.
        list = []
#         print 'checking', j
        for i in range(1, len(k_list)):
            val = (get_percent( k_list[i][idx_open], k_list[i-1][idx_close]))
#             print  val, j
            if (FloatIsEqual(val , j)):
                list.append((get_percent(k_list[i][idx_high],k_list[i][idx_open])))
#                 print 'match'
        if len(list):
            print 'checking', j, 'count', len(list), 'max', max(list), 'min', min(list), 'avg', avg(list)
        
    f.close()
        
def get_price_map_csv():
    k_list = []
    reader = csv.reader(file('table_600036.csv','rb'))
    i = 0
    for row in reader:
        if i == 0:
            i += 1
            k_list.append(row)
        elif (float(row[5]) != 0): #check Volume==0 row.
            k_list.append(row)

    print 'total item ', len(k_list)
    print 'item per line', len(k_list[1])
    
    idx_date = 0;
    idx_close = 4;
    idx_high = 2;
    idx_low = 3;
    idx_open = 1;
    idx_volume = 5;
    
    f = open('tempout.txt', 'w')
    
    for i in range(2, len(k_list)-1):
        string = k_list[i][idx_date] + ', '
        string += str(get_percent_str(k_list[i][idx_open], k_list[i+1][idx_close])) + ', '
        string += str(get_percent_str(k_list[i][idx_high],k_list[i][idx_open])) + ', '
        string += str(get_percent_str(k_list[i][idx_low],k_list[i][idx_open]))
#         print string
#         f.write(string+'\n')
    
    print 'checking', 'count',  'maxHigh', 'minHigh', 'avgHigh'
    fcsv = open('table_out1.csv', 'wb')
    csvWriter = csv.writer(fcsv)

    line = 'percent', 'len(listHigh)',  'max(listHigh)', 'min(listHigh)', 'avg(listHigh)'
    line += '','len(listLow)',  'max(listLow)', 'min(listLow)', 'avg(listLow)'
    csvWriter.writerow(line)
     
    for jj in range(-30, 30, 1):
        j = jj/10.
        listHigh = []
        listLow = []

        print 'checking', j
        for i in range(2, len(k_list)-1):
            val = (get_percent_str( k_list[i][idx_open], k_list[i+1][idx_close]))
#             print  val, j

            if (float('%.1f' % val) == j ):
#                print 'match', k_list[i]
#                print get_percent_str(k_list[i][idx_high],k_list[i][idx_open])
                listHigh.append((get_percent_str(k_list[i][idx_high],k_list[i][idx_open])))
                listLow.append((get_percent_str(k_list[i][idx_low],k_list[i][idx_open])))
#        f.write(str(list)+'\n')
        if len(listHigh) or len(listLow):
            line = float('%.2f' % j), len(listHigh),  max(listHigh), min(listHigh), avg(listHigh)
            line += '', len(listLow),  max(listLow), min(listLow), avg(listLow)
            print  line
            csvWriter.writerow(line)
        
    f.close()
    fcsv.close()
     

def get_gc001_csv():
    k_list = []
    reader = csv.reader(file('table_gc001_6m.csv','rb'))
    i = 0
    for row in reader:
        if i == 0:
            i += 1
        elif (row[5] and float(row[5]) != 0): #check Volume==0 row.
            k_list.append(row)
        i=i+1

    print 'total item ', len(k_list)
    print 'item per line', len(k_list[1])
    
    idx_date = 0;
    idx_close = 4;
    idx_high = 2;
    idx_low = 3;
    idx_open = 1;
    idx_volume = 5;
    
    profile = []
    for i in range(0, len(k_list)):
        profile.append(float(k_list[i][idx_high]))

    print 'checking high'
    print 'days:', len(profile), 'avg:', avg(profile), 'high:', max(profile), 'low:', min(profile)
    print 'Year profile % is', avg(profile)*len(profile)/(365/2)


    profile = []
    for i in range(0, len(k_list)):
        profile.append(float(k_list[i][idx_low]))

    print 'checking low'
    print 'days:', len(profile), 'avg:', avg(profile), 'high:', max(profile), 'low:', min(profile)
    print 'Year profile % is', avg(profile)*len(profile)/(365/2)

def get_stock_list():
    fcsv = open('table_out1.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    
    for code in range(600000, 604100):
        if (code%100 == 0):
            print code
        codestr = ''
        codestr = 'sh' + str(code)
        print codestr
        name, price_current, price_diff, change_percent = get_price(codestr)
        if (name):
#            print code, name
            line = code, name
            csvWriter.writerow(line)
    fcsv.close()

#########################################################################
def get_stock_history_csv(code, name):  
    url = 'http://table.finance.yahoo.com/table.csv?s=' + str(code) +'.ss'
    local = 'data/'+str(code)+'.csv'
    if os.path.exists(local):
        print local, 'exist! skip!'
    else:  
        print 'get csv for', name, ', url:', url
        socket.setdefaulttimeout(2)  
        urllib.urlretrieve(url, local, 0)
        print 'got csv file, size:', os.path.getsize(local), 'bytes!'
        

def get_all_history():
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    error_count = 0    
    for row in reader:
#        print 'code:', row[0], 'name:', row[1]
        try:
            get_stock_history_csv(row[0], row[1])
            error_count = 0
        except:
            print 'get_all_history error'
            error_count = error_count + 1
        if error_count > 10:
            print 'error count gt 10 ! exit !'
            break

#########################################################################
def write_price_map_csv(code, name, history_csv, out_csv, mode):
    k_list = []
    reader = csv.reader(file(history_csv,'rb'))
    i = 0
    for row in reader:
        if i == 0:
            i += 1
            k_list.append(row)
        elif (float(row[5]) != 0): #check Volume==0 row.
            k_list.append(row)

    print name, code, 'Total item:', len(k_list),'item per line:', len(k_list[1])
    
    idx_date = 0;
    idx_close = 4;
    idx_high = 2;
    idx_low = 3;
    idx_open = 1;
    idx_volume = 5;
    
#    print 'checking', 'count',  'maxHigh', 'minHigh', 'avgHigh'
    fcsv = open(out_csv, 'wb')
    csvWriter = csv.writer(fcsv)

    if mode == 1:
        line = 'percent', 'len(listHigh)',  'max(listHigh)', 'min(listHigh)', 'avg(listHigh)'
        line += '','len(listLow)',  'max(listLow)', 'min(listLow)', 'avg(listLow)'
    if mode == 2:
        line = 'percent', 'len(listTclose)',  'max(listTclose)', 'min(listTclose)', 'avg(listTclose)'
        
    csvWriter.writerow(line)
     
    for jj in range(-50, 50, 1):
        j = jj/10.
        listHigh = []
        listLow = []

#        print 'checking', j
        if mode == 1:
            for i in range(2, len(k_list)-1):
                val = (get_percent_str( k_list[i][idx_open], k_list[i+1][idx_close]))   #last close
                if (float('%.1f' % val) == j ):
                    listHigh.append((get_percent_str(k_list[i][idx_high],k_list[i+1][idx_close])))
                    listLow.append((get_percent_str(k_list[i][idx_low],k_list[i+1][idx_close])))
            if len(listHigh) or len(listLow):
                line = float('%.1f' % j), len(listHigh),  max(listHigh), min(listHigh), avg(listHigh)
                line += '', len(listLow),  max(listLow), min(listLow), avg(listLow)
                csvWriter.writerow(line)
                        
        if mode == 2:
            skip_date = True
            skip_count = 0
            for i in range(2, len(k_list)-1):
#                print k_list[i][idx_date]
                if '2012-12-31' == k_list[i][idx_date]:
#                    print k_list[i][idx_date]
                    skip_date = False
                if skip_date:
                    skip_count += 1
                    continue
                val = (get_percent_str( k_list[i][idx_open], k_list[i+1][idx_close]))   #last close
                if (float('%.1f' % val) == j ):
                    percent = (float(k_list[i][idx_close])-float(k_list[i][idx_open])) *100. / float(k_list[i+1][idx_close])
                    listHigh.append(float('%.1f' % percent))
            if len(listHigh):
                line = float('%.1f' % j), len(listHigh),  max(listHigh), min(listHigh), avg(listHigh)
                csvWriter.writerow(line)
#                print 'skip_count', skip_count

    fcsv.close()

# mode 1: guess todayhigh/lastclose based on todayopen/lastclose
# mode 2: guess todayclose/todayopen based on todayopen/lastclose
def get_all_mapfile(mode = 1):
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    total = 0
    for row in reader:
        try:
            code = row[0]
            name = row[1]
            history_csv = 'data/'+str(code)+'.csv'
            if mode == 1:
                out_csv = 'data/'+str(code)+'_map_Lc2Th.csv'    #LastClose -> TodayHigh
            if mode == 2:
                out_csv = 'data/'+str(code)+'_map_To2Tc.csv'    #TodayOpen -> TodayClose

            if os.path.exists(history_csv):
                write_price_map_csv(code, name, history_csv, out_csv, mode)
            total += 1
            print total
#            if total > 2:
#                return
        except:
            print 'get_all_mapfile error'

#########################################################################
def get_rt_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
    try:
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
    except Exception, e:
        return ('', 0., 0, 0.)
    else:
        strs = content.decode('gbk')
        data = strs.split('"')[1].split(',')
#        print data
        name = "%s" % data[0]
        if (name):
            return (name, "%-5s" % float(data[1]), "%-5s" % float(data[2]), "%-5s" % float(data[3]), 
                    "%-5s" % float(data[4]), "%-5s" % float(data[5]))
        else:
            return ('', 0, 0, 0, 0, 0)

def check_history_open_data(map_csv, openprice, lastclose):
    if os.path.exists(map_csv):
        reader = csv.reader(file(map_csv,'rb'))
        val = get_percent_str(openprice, lastclose)
        if val > 5.0:
            val = 5.0
        if val < -5.0:
            val = -5.0
        line =  (0, 0, 0, 0)
        reader.next()
        for row in reader:
            v = float(row[0])
            line = (val, float(row[4]), float(row[9]), int(row[1]))
            if (val > v):
                continue
            if (val <= v):
                return line
                break
#         print 'val', val
        return line

def check_history_open_data_To2Tc(map_csv, openprice, lastclose):
    if os.path.exists(map_csv):
        reader = csv.reader(file(map_csv,'rb'))
        val = get_percent_str(openprice, lastclose)
        if val > 5.0:
            val = 5.0
        if val < -5.0:
            val = -5.0
        line =  (0, 0, 0, 0)
        reader.next()
        for row in reader:
            v = float(row[0])
            line = (val, float(row[4]), int(row[1]))
            if (val > v):
                continue
            if (val <= v):
                return line
                break
#         print 'val', val
        return line
    
def check_all_open():
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    fcsv = open('check_all_open.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    line = 'Code' , 'Name', 'Guess%','Open%','avgH%','tHigh%','avgL%','tLow%', 'RealGuess%', 'count', 'Curr-Open%', '', 'lastclose', 'open', 'curr', 'todayHigh', 'todayLow'    
    csvWriter.writerow(line)
    print 'check_all_open, wait...'
    i = 0
    list = []
    for row in reader:
#        if (i > 10):
#            break;
        i = i+1;
        if (i%100 == 0):
            print i
        try:
            code = row[0]
            name = row[1]
            map_csv = 'data/'+str(code)+'_map.csv'
            if os.path.exists(map_csv):
                name, openprice, lastclose, curr, todayhigh, todaylow = get_rt_price('sh'+code)
                if (float(openprice) and float(lastclose)):
#                    print name, code, open, lastclose, curr, todayhigh, todaylow
                    chg, avgH, avgL, count = check_history_open_data(map_csv, openprice, lastclose)
                    curr_chg = get_percent_str(curr, lastclose)
                    realH_percent = float('%.1f' % (get_percent_str(todayhigh,lastclose) - chg))
                    guess_percent = float('%.1f' % (avgH - chg))
                    curr_percent =  float('%.1f' % (get_percent_str(curr,lastclose)))                    
                    line = (code, (row[1]),
                            guess_percent, chg,
                            float('%.1f' % avgH), get_percent_str(todayhigh,lastclose),
                            float('%.1f' % avgL), get_percent_str(todaylow, lastclose),
                            realH_percent,
                            count, 
                            float('%.1f' % (curr_percent - chg)),
                            '',
                            float('%.2f' % float(lastclose)),
                            float('%.2f' % float(openprice)),
                            float('%.2f' % float(curr)),
                            float('%.2f' % float(todayhigh)),
                            float('%.2f' % float(todaylow))
                            )
                    if (avgH and count):
                        list.append(line)
        except:
            print 'check_all_open error'
            
    print "*** Result ***"
    print len(list), len(list[0])
    list.sort(key=lambda data : data[2], reverse=True)
    print 'sorted.'
    i = 0
    print 'Code' , 'Name', 'Guess%','Open%','avgH%','tHigh%','avgL%','tLow%', 'RealHighProfit%', 'count', 'CurrHighProfit%'
    for line in list:
        csvWriter.writerow(line)
#        if (i < 20):
#            print line
        i = i + 1
    fcsv.close()
    
    # highlight one
    maintext = "\n"
    total = 0
    for oneline in list:
        if total >= 10:
            break;
        code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open_gap, space1, lastclose, openprice, curr_price, todayHigh, todayLow = oneline
        if todayl < avgl or todayh > avgh:
            maintext += str(oneline) 
            maintext += '\n\t\tCurr:' + str(get_percent_str(float(curr_price), float(lastclose)))+'%,'
            maintext += 'Curr-avgL:' + str(get_percent_str(float(curr_price), float(lastclose)) - float(avgl)) +'%,'
            maintext += 'Curr-avgH:' + str(get_percent_str(float(curr_price), float(lastclose)) - float(avgh)) +'%,'
            maintext += name + "\n"
            total += 1

    print maintext
    return maintext
              
def list_lastclose_add(list, code, lastclose):
#    print code, lastclose, len(list)
    for i in range(len(list)):
        if (list[i][0] == code):
            list[i] = [code, lastclose]
#            print 'lastclose list change.', code
            return
    list.append([code, lastclose])
#    print 'lastclose list append'

        
def list_lastclose_get_lastclose(list, code):
    for i in range(len(list)):
        if (list[i][0] == code):
            return list[i][1]
    return 0 
                      
  
def get_day_history_csv():
    bak_lastclose = []
    for year in range(2012, 2014, 1):
        for month in range(1, 12+1):
            for day in range (1, 31+1):
                date_str = str(year)+'-'+str('%02d' % month)+'-'+str('%02d' % day)
                print date_str
                try:
                    if (datetime.datetime(year,month,day).weekday() > 4):
                        print 'skip weekend.'
                        continue
                except ValueError:
                    print 'invalid date'
                    continue
                if os.path.exists('data/'+date_str+'.csv'):
                    print 'already done.'
                    continue
                reader = csv.reader(file('table_stocklist_sh.csv','rb'))
                count = 0
                index = 0
                for row_code in reader:
                    code = row_code[0]
                    name = row_code[1]
                    data_csv = 'data/'+str(code)+'.csv'
                    # when no found in 10 stock history. means this date may be big holiday
                    # so, skip the rest stock.
                    if (count == 0 and index > 10):
                        print 'big holiday!'
                        break
                    else:
                        index = index + 1
                    
                    if os.path.exists(data_csv):
                        reader_data = csv.reader(file(data_csv,'rb'))
#                        print 'checking file', data_csv
                        for row_data in reader_data:
                            try:
                                if (row_data[0] and str(row_data[0]) == date_str and float(row_data[5]) != 0):
                                    closeprice = float(row_data[4])
                                    if (count == 0):
                                        fcsv = open('data/'+date_str+'.csv', 'wb')
                                        csvWriter = csv.writer(fcsv)
                                        line = 'Code' , 'Name', 'Date' ,'Open','High','Low','Close','Volume','Adj Close', 'LastClose'
                                        csvWriter.writerow(line)                                
                                    row_data.insert(0, code)
                                    row_data.insert(1, name)
                                    row_data.append(list_lastclose_get_lastclose(bak_lastclose, code))
                                    csvWriter.writerow(row_data)
                                    count = count + 1
                                    list_lastclose_add(bak_lastclose, code, closeprice)
#                                    print len(bak_lastclose),  bak_lastclose
                                    break
                            except IndexError:
                                break
                print 'total items', count
                if (count):
                    fcsv.close()
    print 'done!'               
                        
  
def get_guess_realH_count():
    cnt1 = 0
    list = []
    fcsv = open('data/'+'realH_count_10y_all'+'.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    line = 'Code' , 'Name', 'Date' ,'Guess%','Open%','avgH%','tHigh%','avgL%','tLow%', 'RealHighProfit%', 'count'
    csvWriter.writerow(line)         
    for year in range(2000, 2014, 1):
        for month in range(1, 12+1):
            for day in range (1, 31+1):
                list = []
#                if cnt1 > 10:
#                    break;
                cnt1 = cnt1 + 1
                date_str = str(year)+'-'+str('%02d' % month)+'-'+str('%02d' % day)
                print date_str
                try:
                    if (datetime.datetime(year,month,day).weekday() > 4):
                        print 'skip weekend.'
                        continue
                except ValueError:
                    print 'invalid date'
                    continue
                date_csv = 'data/'+date_str+'.csv'
                if not os.path.exists(date_csv):
                    print 'no data file.'
                    continue                        
                reader = csv.reader(file(date_csv,'rb'))
                reader.next()
                count = 0
                bFirst = True
                for line in reader:
                    if bFirst:
                        bFirst = False
                        continue
                    if len(line) < 10:
                        continue
                    code = line[0]
                    name = line[1]
                    openprice = float(line[3])
                    todayhigh = float(line[4])
                    todaylow = float(line[5])
#                    print code, openprice, todayhigh
                    lastclose = float(line[9])
#                    print code, openprice, todayhigh, lastclose
                    map_csv = 'data/'+str(code)+'_map.csv'
                    if os.path.exists(map_csv):
                        if (openprice and lastclose):
                            chg, avgH, avgL, count = check_history_open_data(map_csv, openprice, lastclose)
                            realH_percent = get_percent_str(todayhigh,lastclose) - chg
                            guess_percent = float('%.1f' % (avgH - chg)) 
                            line = (code, name, date_str,
                                    guess_percent, chg,
                                    avgH, get_percent_str(todayhigh,lastclose),
                                    avgL, get_percent_str(todaylow,lastclose), 
                                    realH_percent, 
                                    count
                                    )
                            if (avgH and count > 3 and guess_percent > 2.5 and realH_percent > 4.0):
                                list.append(line)
#                                print line, (todayhigh-openprice), lastclose
                                
                list.sort(key=lambda data : data[3], reverse=True)
                print 'sorted....................', len(list)
                i = 0
                for line in list:
                    if (i > 20):
                        break
                    i = i + 1
                    csvWriter.writerow(line)
#                    print line[1], line[0], 'guess%', line[2], 'open%', line[3], 'avgH', line[4], \
#                            'tHigh', line[5], 'RealHigh%', line[6], 'count', line[7]
                                            
def analyze_realH_count():                    
    reader = csv.reader(file('data/realH_count_10y_all.csv','rb'))
    reader.next()
    count = 0
    list = []
    for readline in reader:
#        if (count > 15):
#            break
        count = count + 1
        line = (float('%.1f' % float(readline[9])), float(readline[10]))
        list.append(line)
    print list
    list1=[]
    list2=[]
    for realH,cnt in list:
        list1.append(realH)
        list2.append(cnt)
    print 'cnt', max(list2), min(list2)
    print 'realH', max(list1), min(list1)
    checkv = min(list1)
    while(1):
#        print checkv
        total = 0
        templist = []
        for realH,cnt in list:
#            print 'checking', checkv, realH
            if (str(realH) == str(checkv)):
#                print 'Equal !!!'
                total = total + 1
                templist.append(cnt)
        if (total):
#            print templist
            print 'Checking', checkv, 'total', total, 'avgCnt', avg(templist)

        checkv = checkv + 0.1
        if checkv > max(list1):
            break
            
    print 'done!'
    
#name, openprice, lastclose, curr, todayhigh, todaylow    
def get_history_price(date_csv, check_code):        
    reader = csv.reader(file(date_csv,'rb'))
    reader.next()
    count = 0
    for line in reader:
        if len(line) < 10:
            continue
        if (check_code == line[0]):
            code = line[0]
            name = line[1]
            openprice = float(line[3])
            todayhigh = float(line[4])
            todaylow = float(line[5])
            todayclose = float(line[6])
            lastclose = float(line[9])
            return (name, "%-5s" % openprice, "%-5s" % lastclose, "%-5s" % todayclose, 
                "%-5s" % todayhigh, "%-5s" % todaylow)
#    print 'get_history_price failed.', check_code
    return ('', 0, 0, 0, 0, 0)
  
def get_history_price_from_list(todaylist, check_code):
    for row in todaylist:
        code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open, space1, lastclose, openprice, todayclose, todayhigh, todaylow = row
        if len(row) < 10:
            continue
        if (check_code == code):
#             print code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open, space1, lastclose, openprice, todayclose, todayhigh, todaylow
            return (name, "%-5s" % openprice, "%-5s" % lastclose, "%-5s" % todayclose, 
                "%-5s" % todayhigh, "%-5s" % todaylow)
#    print 'get_history_price failed.', check_code
    return ('', 0, 0, 0, 0, 0)    

# Creat data/check_all_open_20130101.csv files if not exist. and return the list in csv.    
def check_all_open_from_history(date_str, date_csv, mode = 1):
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    filename = 'data/check_all_open_'+date_str+'.csv'
    if mode == 2:
        filename = 'data/check_all_open_To2Tc_'+date_str+'.csv'
    if os.path.exists(filename):
        print 'get data from', filename
        list = []
        lists = csv.reader(file(filename,'rb'))
        lists.next()
        for row in lists:
#            print row
            line = (row[0], row[1],
                    float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[6]),
                    float(row[7]),float(row[8]),float(row[9]),float(row[10]),row[11],
                    float(row[12]), float(row[13]), float(row[14]), float(row[15]), float(row[16])
                            )
            list.append(line)
        return list

    filename = 'data/check_all_open_'+date_str+'_1500.csv'
    if os.path.exists(filename) and mode == 1:
        print 'check more file: ',filename
        print 'get data from', filename
        list = []
        lists = csv.reader(file(filename,'rb'))
        lists.next()
        for row in lists:
#            print row
            if len(row) == 15:
                line = (row[0], row[1],
                        float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[6]),
                        float(row[7]),float(row[8]),float(row[9]),float(row[10]),row[11],
                        float(row[12]), float(row[13]), float(row[14]), 0, 0)
            else:
                line = (row[0], row[1],
                        float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[6]),
                        float(row[7]),float(row[8]),float(row[9]),float(row[10]),row[11],
                        float(row[12]), float(row[13]), float(row[14]), float(row[15]), float(row[16])
                            )
            list.append(line)
        return list
    
    # Not Exist, creat it!
    filename = 'data/check_all_open_To2Tc_'+date_str+'.csv'    
    fcsv = open(filename, 'wb')
    csvWriter = csv.writer(fcsv)
    line = 'Code' , 'Name', 'Guess%','Open%','avgH%','tHigh%','avgL%','tLow%', 'RealGuess%', 'count', 'Curr-Open%', '',\
            'lastclose', 'openprice', 'todayclose', 'todayHigh', 'todayLow', date_csv
    if mode == 2:
        line = 'Code' , 'Name', 'Guess%','Open%','avgTo2Tc%','NULL','NULL','NULL', 'Close%', 'count', 'Close-Open%', '',\
                'lastclose', 'openprice', 'todayclose', 'todayHigh', 'todayLow', date_csv
            
    csvWriter.writerow(line)
    print 'check_all_open_from_history, wait...'
    i = 0
    list = []
    for row in reader:
#        if (i > 10):
#            break;
        i = i+1;
        if (i%100 == 0):
            print i,'...',
        try:
            code = row[0]
            name = row[1]
            if mode == 1:
                map_csv = 'data/'+str(code)+'_map_Lc2Th.csv'
                if os.path.exists(map_csv) and os.path.exists(date_csv):
                    name, openprice, lastclose, curr, todayhigh, todaylow = get_history_price(date_csv, code)
    #                 if (code == '600844'):
    #                     print name, openprice, lastclose, curr, todayhigh, todaylow 
                    if (float(openprice) and float(lastclose)):
    #                    print name, code, open, lastclose, curr, todayhigh, todaylow
                        chg, avgH, avgL, count = check_history_open_data(map_csv, openprice, lastclose)
    #                    if (code == '600315'):
    #                        print chg, avgH, avgL, count                    
                        curr_chg = get_percent_str(curr, lastclose)
                        realH_percent = float('%.1f' % (get_percent_str(todayhigh,lastclose) - chg))
                        guess_percent = float('%.1f' % (avgH - chg))
                        curr_percent =  float('%.1f' % (get_percent_str(curr,lastclose)))                    
                        line = (code, (row[1]),
                                guess_percent, chg,
                                float('%.1f' % avgH), get_percent_str(todayhigh,lastclose),
                                float('%.1f' % avgL), get_percent_str(todaylow, lastclose),
                                realH_percent,
                                count, 
                                float('%.1f' % (curr_percent - chg)),
                                '',
                                float(lastclose),
                                float(openprice),
                                float(curr),
                                float(todayhigh),
                                float(todaylow)
                                )
    #                     if (code == '600844'):
    #                         print line
                        if (avgH and count):
                            list.append(line)
            if mode == 2:
                map_csv = 'data/'+str(code)+'_map_To2Tc.csv'
                if os.path.exists(map_csv) and os.path.exists(date_csv):
                    name, openprice, lastclose, todayclose, todayhigh, todaylow = get_history_price(date_csv, code)
    #                 if (code == '600844'):
#                    print name, openprice, lastclose, todayclose, todayhigh, todaylow 
                    if (float(openprice) and float(lastclose)):
    #                    print name, code, open, lastclose, curr, todayhigh, todaylow
                        open_percent, avgTo2Tc, count = check_history_open_data_To2Tc(map_csv, openprice, lastclose)
    #                    if (code == '600315'):
#                        print code, open_percent, avgTo2Tc, count, 'check_history_open_data_To2Tc'                    
                        curr_chg = get_percent_str(todayclose, lastclose)
                        realH_percent = float('%.1f' % (get_percent_str(todayclose,lastclose) - open_percent))
                        guess_percent = float('%.1f' % (avgTo2Tc))
#                        curr_percent =  float('%.1f' % (get_percent_str(curr,lastclose)))    
                        line = (code, (row[1]),
                                guess_percent, open_percent,
                                float('%.1f' % avgTo2Tc), 0,
                                0, 0,
                                float('%.1f' % (get_percent_str(todayclose,lastclose))),
                                count, 
                                realH_percent,
                                '',
                                float(lastclose),
                                float(openprice),
                                float(todayclose),
                                float(todayhigh),
                                float(todaylow)
                                )
    #                     if (code == '600844'):
#                        print line
                        if (avgTo2Tc and count):
                            list.append(line)                
        except:
            print 'check_all_open_from_history error'
            
    print "*** Result ***",
    print 'Items:', len(list), 
    if (len(list)):
        print 'Field:', len(list[0])
    list.sort(key=lambda data : data[2], reverse=True)
#    print 'sorted.'
    i = 0
#    print 'Code' , 'Name', 'Guess%','Open%','avgH%','tHigh%','avgL%','tLow%', 'RealHighProfit%', 'count', 'CurrHighProfit%'
    for line in list:
#        if (i < 200):
        csvWriter.writerow(line)
#            print line
        i = i + 1
    fcsv.close() 
    return list       
        
def do_trade_emulator(mode = 1):
    global myhold

    fcsv = open('do_trade_emulator.csv', 'wb')
    csvWriter = csv.writer(fcsv)
    cnt1 = 0
    myhold_init(100*10000)
    print myhold
    for year in range(2013, 2014, 1):
        for month in range(4, 12+1):
            for day in range (1, 31+1):
                list = []
#                 if cnt1 > 5:
#                     break;
                cnt1 = cnt1 + 1
                date_str = str(year)+'-'+str('%02d' % month)+'-'+str('%02d' % day)
                print date_str,
                try:
                    if (datetime.datetime(year,month,day).weekday() > 4):
                        print 'skip weekend.'
                        continue
                except ValueError:
                    print 'invalid date'
                    continue
                date_csv = 'data/'+date_str+'.csv'    
                if not os.path.exists(date_csv) and not os.path.exists('data/check_all_open_'+date_str+'_1500.csv'):
                    print 'no data file.'
                    continue                        
                today_list = check_all_open_from_history(date_str, date_csv, mode)
#                print today_list
                myhold_to_sell = myhold[:]
                funds = 10*1000
                if len(myhold_to_sell):
#                    print 'need sell now!'
                    sell_chg_array = []
                    for code,buyprice,amount,buyname in myhold_to_sell:
#                        print 'try to sell', code
#                         name, openprice, lastclose, currX, todayhigh, todaylow = get_history_price(date_csv, code)
#                         print 'get_history_price', name, openprice, lastclose, currX, todayhigh, todaylow 
                        name, openprice, lastclose, currX, todayhigh, todaylow = get_history_price_from_list(today_list, code)
#                        print 'get_history_price_from_list', name, openprice, lastclose, currX, todayhigh, todaylow 
                        
                        if openprice:
                            sellprice = float(openprice)
#                            myhold_sell(code, (float(todaylow)+float(todayhigh))/2, float(amount))
                            myhold_sell(code, sellprice, float(amount), name)
                            print '--------------- sell price chg%', get_percent_str(sellprice, buyprice)
                            sell_chg_array.append(get_percent_str(sellprice, buyprice))
#                        print myhold
                    if True:
                        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> avg chg % is ', avg(sell_chg_array), '%!'
                        totalcash, total = myhold_listall()
                        line = date_str, avg(sell_chg_array), totalcash, total
                        csvWriter.writerow(line)
                        if avg(sell_chg_array) >= 2.0:
                            funds *= 2
#                if len(myhold) == 0:
                if True:
#                    print 'need buy some.'
                    weekday  = datetime.datetime(year,month,day).weekday()
                    buylists = choose_one2buy(today_list, weekday)
                    for buylist in buylists:
                        code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open, space1, lastclose, openprice, todayclose, todayHighPrice, todayLowPrice = buylist
#                        buyprice = lastclose * (1.0 + ((avgl+todayl)/2)/100.)
                        buyprice = openprice
#                        print buyprice, openprice
#                         myhold_buy(buylist[0], openprice, int(10000/openprice))
                        myhold_buy(buylist[0], buyprice, int(funds/buyprice), name)
                myhold_listall()
    myhold_listall()
    fcsv.close()
    print 'done!'

def choose_one2buy(today_list, weekday):
    global buy_max
    buylists = []
    if len(today_list) == 0:
        return []

#     if True:
#         total = 3
#         while(total):
#             index = random.randint(0, len(today_list)-1)
#             print index, len(today_list)
#             buylists.append(today_list[index])
#             total = total - 1
#         return buylists

    total = 0
    for list in today_list:
        code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open, space1, lastclose, openprice, todayclose, todayHighPrice, todayLowPrice = list
        if 20 > count >= 1 and 2.0 > open_percent > -3.0 and guess < 6 :#and todayl <= avgl:
            print list
            buylists.append(list)
            total = total + 1
        if total ==3:
            break
    return buylists

mycash = 0
myhold=[]
def myhold_init(value):
    global mycash
    global myhold
    mycash = value
    myhold = []   
    print 'init. mycash', value

def myhold_get_cashsize():
    global mycash
    global myhold
    print 'mycash', mycash
    return mycash

def myhold_listall():
    global mycash
    global myhold
    market_value = 0    
    print '*************** list ****************'
    
    for code,price,amount, codename in myhold:
        if (code and price and amount):
            print 'list',code,price,amount, codename
            market_value = market_value + price*amount
    print 'Cash:', int(mycash), ', Total:', int(mycash + market_value)
    print '***************************************'
    return int(mycash), int(mycash + market_value)
        
def myhold_buy(code, price, amount, name = None):
    global mycash
    global myhold
    if ((price*amount)*1.002) < mycash:
        line = (code, price, amount, name)
        myhold.insert(0, line)
        mycash = mycash - (price*amount)*(1. + 0.002)
        print 'buy', line, name
    else:
        print 'buy,out of cash!'

def myhold_sell(code, price, sell_amount, name = None):
    global mycash
    global myhold
    for i in range(0,len(myhold)):
        if myhold[i][0] == code:
            code,buyprice,amount, name = myhold[i]
            print 'sell', code, price, sell_amount, name
            if sell_amount <= amount:
                mycash = mycash + price*sell_amount*(1. - 0.002)
                if  sell_amount < amount:
                    line = (code, buyprice,  amount - sell_amount)
                    del myhold[i]
                    myhold.insert(0, line)                    
                else:
                    del myhold[i]
                return
    print 'sell failed.'  

def do_test_myhold():
    myhold_init(10*10000)
    myhold_listall()
    myhold_buy('11', 4.5, 1000)
    myhold_listall()
    myhold_buy('12', 5.5, 200)
    myhold_listall()
    myhold_sell('13', 1.1, 200)
    myhold_listall()
    myhold_sell('11', 4.8, 800)
    myhold_listall()
    myhold_sell('12', 5.6, 200)
    myhold_listall()
        
def trader_mainloop():
    print 'enter trader_mainloop.'



'''
how init the data.
step by step.
1. use --3 to download 6000030.csv
2. use --7 to get csv by date.  2006-03-29.csv
3. use --8 to get stock price map.csv, call get_all_mapfile()
'''
                        
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
if  __name__ == '__main__':
    if len(sys.argv)<2:
        print 'No action specified.'
        print '--1: test_StockSmart'
        print '--2: stock_daemon'
        print '--3: get_price_map'
        print '--4: get_price_map from .csv'
        sys.exit()
            
    if sys.argv[1].startswith('--'):
        option=sys.argv[1][2:]            
        # fetch sys.argv[1] but without the first two characters
        if option=='1':
            test_StockSmart()
        elif option=='2':
            stock_daemon()    
        elif option=='3':
            get_all_history()
        elif option=='4':
            get_price_map_csv()
        elif option=='5':
            get_stock_list()()
        elif option=='6':
            check_all_open()
        elif option=='7':
            get_day_history_csv()
        elif option=='8':
            get_all_mapfile(2)
        elif option=='9':
            analyze_realH_count()
        elif option=='10':
            trader_mainloop()
        elif option=='11':
            for i in range(0, 1):
                print 'BUY_MAX', buy_max, 'START!'
                do_trade_emulator(2)
                print 'BUY_MAX', buy_max, 'END!'
                buy_max = buy_max + 1 
            
    print 'main done!'
    beep_sos()
