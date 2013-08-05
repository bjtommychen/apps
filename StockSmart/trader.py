import win32clipboard as clip
import win32con
import time

from StockSmart import *
from Gtalk_test import *
from mail_process import *
from main import *

todaybuylist = []

def clip_getText():
    clip.OpenClipboard()
    clip.OpenClipboard()
    d = clip.GetClipboardData(win32con.CF_TEXT)
    clip.CloseClipboard()
    return d

def clip_setText(aString):
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardData(win32con.CF_TEXT, aString)
    clip.CloseClipboard()

def trader_sendcmd(cmd):
    print 'trader_sendcmd:', cmd
    if False:
        return
    clip_setText(cmd)
    max_time_wait = 30   # Min. set to 10s. as we can't guarantee to completed in < 10s 
    while True:
        if clip_getText() == "ok":
            break
        time.sleep(1)
        max_time_wait -= 1
        if max_time_wait == 0:
            break
                 
def trader_cmd_buy(code, price, cnt):
            cmdstr = "trader|" + "buy|" + str(code) + '|'+str(price)+'|'+str(cnt)
            trader_sendcmd(cmdstr)    

def trader_cmd_sell(code, price, cnt):
            cmdstr = "trader|" + "sell|" + str(code) + '|'+str(price)+'|'+str(cnt)
            trader_sendcmd(cmdstr)    

def trader_cmd_buyflash(code, cnt):
            cmdstr = "trader|" + "buyflash|" + str(code) + '|'+str(cnt)
            trader_sendcmd(cmdstr)    

def trader_cmd_sellflash(code, cnt):
            cmdstr = "trader|" + "sellflash|" + str(code) + '|'+str(cnt)
            trader_sendcmd(cmdstr)    

            
def trader_check_all_open():
#based on check_all_open():
    reader = csv.reader(file('table_stocklist_sh.csv','rb'))
    print 'trader_check_all_open, wait...'
    i = 0
    list = []
    for row in reader:
#        if (i > 100):
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
                            )
                    if (avgH and count > 4):
                        list.append(line)
        except:
            print 'error'
            
    print "*** Result ***"
    print 'items:', len(list), 'column:', len(list[0])
    list.sort(key=lambda data : data[2], reverse=True)
    print 'sorted. by guess_percent.'
    i = 0
#    print 'Code' , 'Name', 'Guess%','Open%','avgH%','tHigh%','avgL%','tLow%', 'RealHighProfit%', 'count', 'CurrHighProfit%'
    # highlight one
    maintext = "\n"
    return list

def choose_one2buy(today_list):
    global buy_max
    buylists = []
    if len(today_list) == 0:
        return []

    total = 0
    for list in today_list:
        code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open, space1, lastclose, openprice, currPrice = list
        if 20 > count >= 1 and 2.0 > open_percent > -3.0 and guess < 6 :#and todayl <= avgl:
            print list
            buylists.append(list)
            total = total + 1
        if total ==3:
            break
    return buylists
                 
def traderDo_at926():
    global todaybuylist
    global report_text
    maintext = ""
    print 'enter traderDo_at926'
    todaybuylist = choose_one2buy(trader_check_all_open())
    maintext += 'today buy list ready, total ' + str(len(todaybuylist)) + '\n'
    report_text += maintext
    return maintext
#    print todaybuylist
    
def traderDo_at930():
    global todaybuylist
    global report_text
    print 'enter traderDo_at930'
    maintext = ""
    if os.path.exists("myholds.csv"):
        reader = csv.reader(file('myholds.csv','rb'))
        print 'stock need to sell '
        for row in reader:
            trader_cmd_sellflash(row[0], row[1])
            maintext += 'sellflash.' + str(row[0]) + ' ' + str(row[1]) + '\n'
                
    fcsv = open('myholds.csv', 'wb')
    csvWriter = csv.writer(fcsv)                
    funds = 3*1000
    for buyone in todaybuylist:
        code, name, guess, open_percent, avgh, todayh, avgl, todayl, realguess, count, curr_open, space1, lastclose, openprice, currprice = buyone
        cnt = int((funds/currprice)/100)*100
        cnt = 100 # THIS IS FOR DEBUG    
        trader_cmd_buyflash(code, cnt)
        csv_line = code, cnt, currprice
        csvWriter.writerow(csv_line)
        maintext += 'buyflash.' + str(csv_line) + '\n'
    fcsv.close()
    report_text += maintext
    return maintext

def trader_check_time(checkstr, reftime):
    if reftime == "" :
        url = 'http://hq.sinajs.cn/?list=sh000001'
        try:
            req = urllib2.Request(url)
            content = urllib2.urlopen(req).read()
        except Exception, e:
            return False
        else:
            strs = content.decode('gbk')
            data = strs.split('"')[1].split(',')    
        currtime = data[31]
    else:
        currtime = reftime
    print currtime
    if checkstr in currtime:
        return True
    else:
        return False

trade_step = 0
trade_debug_timer = 0
report_text = ''
def do_trade_auto():
    global trade_step
    global trade_debug_timer
    global report_text
    if trade_debug_timer == 0:
        trader_showinfo('AutoTrader commander ready !')
    trader_sendcmd("trader|laptop d620")
#    trade_debug_timer += 1
    print 'trade_debug_timer', trade_debug_timer
    msg = ''
    if trader_check_time("9:26:", "") or trade_debug_timer == 1:
        if trade_step == 0:
            report_text = ''
            msg += traderDo_at926()
            trade_step = 1
    if trader_check_time("9:28:", "") or trade_debug_timer == 2:
        if trade_step == 1:
            msg += traderDo_at930()
            send_mail("AutoBuySell at MarketOpen done!", report_text, None)
            trade_step = 2
    if trader_check_time("09:40:", "") or trade_debug_timer == 3:
        if trade_step == 2:
            trade_step = 0
            trade_debug_timer = 0
            if trade_debug_timer == 3:
                os.system('shutdown -s -f -t 600')

    if not msg == '':
        trader_showinfo(msg)
    return 
         
def trader_showinfo(str):
    print str
#     Gtalk_send(str)         
         
def test_autotrade():
    while True:
        do_trade_auto()
        time.sleep(10)
                                   
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
if  __name__ == '__main__':
    print 'trader start.'
    time.sleep(.1)
    if True:
        content = clip_getText()
        print "The content in clipboard is: '%s'." %content
    #    clip_setText("logon")
        time.sleep(1)
#         for i in range(1, 10):
#             cmdstr = "trader|" + "buy|" + str(600080+i) + '|'+str(.01*i)+'|'+str(i*100)
#             trader_sendcmd(cmdstr)
#             print i, ' ', cmdstr
#     
#         for i in range(1, 10):
#             cmdstr = "trader|" + "sell|" + str(600050+i) + '|'+str(10*i)+'|'+str(i*100)
#             trader_sendcmd(cmdstr)
#             print i, ' ', cmdstr
    
#     traderDo_at926()
#     traderDo_at930()
    test_autotrade()
    
    