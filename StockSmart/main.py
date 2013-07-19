
import time
import sys
import os
import socket
import math
import csv

from StockSmart import *
from Gtalk_test import *
from mail_process import *

code_list = ['sh600036', 'sh601328']

#windows: GBK
#ubuntu: ascii
print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')
#sys.setdefaultencoding('ascii')

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
    text = time.strftime("%H:%M", time.localtime())
    if text > '09:20' and text <= '11:30':
        checkopen = True
    elif text >= '13:00' and text <= '15:00':
        checkopen = True
#    print text, checkopen,
    return checkopen

def stock_daemon():
    '''Get the price of stock list, then send it out through Gtalk.
    
    No arguments. '''
    price_old = 0.0
    inited = False
    market_open = False
    
    Gtalk_enable_send(True)
    Gtalk_send("stock_daemon v1.0 Online." + socket.gethostname())
    text = ''
    try:
        while True:
            index = 0
            diff = False
            
            if market_open != check_market_open():
                price_old = 0.
                market_open = check_market_open()
            text = ''
            #get time
            text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + ' '
            if not market_open:
                text += 'Close'
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
            if diff:# or True:
                Gtalk_send(text)
#            else:
#                print 'same ',
            time.sleep(15)
            if not Gtalk_isRunning():
                Gtalk_send("Gtalk sleep, wakeup it!")
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
    for row in reader:
#        print 'code:', row[0], 'name:', row[1]
        try:
            get_stock_history_csv(row[0], row[1])
        except:
            print 'error'

#########################################################################
def write_price_map_csv(code, name, history_csv, out_csv):
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

    line = 'percent', 'len(listHigh)',  'max(listHigh)', 'min(listHigh)', 'avg(listHigh)'
    line += '','len(listLow)',  'max(listLow)', 'min(listLow)', 'avg(listLow)'
    csvWriter.writerow(line)
     
    for jj in range(-50, 50, 1):
        j = jj/10.
        listHigh = []
        listLow = []

#        print 'checking', j
        for i in range(2, len(k_list)-1):
            val = (get_percent_str( k_list[i][idx_open], k_list[i+1][idx_close]))   #last close

            if (float('%.1f' % val) == j ):
                listHigh.append((get_percent_str(k_list[i][idx_high],k_list[i+1][idx_close])))
                listLow.append((get_percent_str(k_list[i][idx_low],k_list[i+1][idx_close])))
        if len(listHigh) or len(listLow):
            line = float('%.1f' % j), len(listHigh),  max(listHigh), min(listHigh), avg(listHigh)
            line += '', len(listLow),  max(listLow), min(listLow), avg(listLow)
#            print  line
            csvWriter.writerow(line)
    fcsv.close()

def get_all_mapfile():
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    for row in reader:
        try:
            code = row[0]
            name = row[1]
            history_csv = 'data/'+str(code)+'.csv'
            out_csv = 'data/'+str(code)+'_map.csv'
            if os.path.exists(history_csv):
                write_price_map_csv(code, name, history_csv, out_csv)
        except:
            print 'error'

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

def check_history_open_data(map_csv, open, lastclose):
    if os.path.exists(map_csv):
        reader = csv.reader(file(map_csv,'rb'))
        val = get_percent_str(open, lastclose)
#        print 'val', val
#        print type(val)
        i = 0
        for row in reader:
            if i == 0:
                i = 1
                continue
            v = float(row[0])
#            print type(v), v
            if (val == v):
#                print row[0], 'avgHigh', row[4], 'avgLow', row[9]
                return  (val, float(row[4]), float(row[9]), int(row[1]))
                break
#                print 'avgHigh', row[4], 'avgLow', row[9], '<======================'
#            print row[0], 'avgHigh', row[4], 'avgLow', row[9]
        return  (0, 0, 0, 0)
    
def check_all_open():
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    i = 0
    listHigh = []
    listName = []
    list = []
    
    print 'check_all_open, wait...'
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
                name, open, lastclose, curr, todayhigh, todaylow = get_rt_price('sh'+code)
                if (float(open)):
#                    print name, code, open, lastclose, curr, todayhigh, todaylow
                    chg, avgH, avgL, count = check_history_open_data(map_csv, open, lastclose)
                    curr_chg = get_percent_str(curr, lastclose)
                    if (avgH and count <= 10):
                        line = (code, name,
                                float('%.1f' % (avgH - chg)), 
                                get_percent_str(open,lastclose), avgH, 
                                float(todayhigh), get_percent_str(todayhigh,lastclose),
                                count
                                ) 
                        list.append(line)
#                        print 'possible profit', (avgH - chg)
        except:
            print 'error'
            
    print "*** Result ***"
    print len(list), len(list[0])
#    print 'index is', listHigh.index(max(listHigh)), 'so it is', listName[listHigh.index(max(listHigh))]
    list.sort(key=lambda data : data[2], reverse=True)
    print 'sorted.'
    i = 0
    for line in list:
        if (i > 20):
            break
        i = i + 1
        print line[1], line[0], 'guess%', line[2], 'open%', line[3], 'avgH', line[4], \
                'tHigh', line[5], 'RealHigh%', line[6] - line[3], 'count', line[7]
                        
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
            get_price_map()
        elif option=='4':
            get_price_map_csv()
        elif option=='5':
            get_stock_list()()
        elif option=='6':
            check_all_open()
    print 'main done!'
