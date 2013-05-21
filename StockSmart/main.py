
import time
from StockSmart import *
from Gtalk_test import *

code_list = ['sh600036', 'sh601328']

print 'System Default Encoding:',sys.getdefaultencoding()

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
    text = ''
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
            name, price_current, change_percent = get_price(code)
            if price_current == 0.:
                print 'get price failed!'
                break
            if index == 0:
                if price_old == 0.:
                    price_old = price_current
                    Gtalk_send("stock_daemon v1.0 Online.")
                    diff = True
                if price_current != price_old:
                    diff_ppk = abs((price_current - price_old)*1000/price_old)
                    print 'diff_ppk is', diff_ppk,
                    diff = diff_ppk > 2
                if diff:
                    price_old = price_current
            text += '%s: %s, %s%%' %(name,price_current,change_percent)
            text += '\n'
            index += 1    
        if diff:# or True:
            Gtalk_send(text)
        else:
            print 'same ',
        time.sleep(15)
        
if  __name__ == '__main__':
    #test_StockSmart()
    stock_daemon()        