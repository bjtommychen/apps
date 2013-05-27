
import time
import sys
import os
import socket
import math
import csv

from StockSmart import *
from Gtalk_test import *

code_list = ['sh600036', 'sh601328']

#windows: GBK
#ubuntu: ascii
print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf8')


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
    print text, checkopen,
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
                        print 'diff_ppk is', diff_ppk,
                        diff = diff_ppk > 2
                    if diff:
                        price_old = price_current
                text += '%s: %s, %s, %s%%' %(name,price_current, price_diff, change_percent)
                text += '\n'
                index += 1    
            if diff:# or True:
                Gtalk_send(text)
            else:
                print 'same ',
            time.sleep(15)
            if not Gtalk_isRunning():
                Gtalk_send("Gtalk sleep, wakeup it!")
    except KeyboardInterrupt:
        print 'Exception!'
    finally:
        Gtalk_exit()
        time.sleep(1)
     
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
        elif (float(row[5]) != 0):
            k_list.append(row)

    print len(k_list)
    print len(k_list[1])
    
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
    
    print 'checking', 'count',  'max', 'min', 'avg'
    fcsv = open('table_out1.csv', 'wb')
    csvWriter = csv.writer(fcsv) 
    for jj in range(-30, 30, 1):
        j = jj/10.
        list = []

        print 'checking', j
        for i in range(2, len(k_list)-1):
            val = (get_percent_str( k_list[i][idx_open], k_list[i+1][idx_close]))
#             print  val, j
            if (FloatIsEqual(val , j)):
                print 'match', k_list[i]
                print get_percent_str(k_list[i][idx_high],k_list[i][idx_open])
                list.append((get_percent_str(k_list[i][idx_high],k_list[i][idx_open])))
        f.write(str(list)+'\n')
        if len(list):
            line = j, len(list),  max(list), min(list), avg(list)
            print  line
            csvWriter.writerow(line)
        
    f.close()
    fcsv.close()
     
        
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
    print 'main done!'
