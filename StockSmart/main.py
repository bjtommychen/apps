
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

def stock_daemon():
    price_old = 0.0

    text = ''
    while True:
        index = 0
        diff = False
        text = ''
        text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + '\n'
        for code in code_list:
            name, price_current, change_percent = get_price(code)
            if index == 0:
                diff = price_current != price_old
                if diff:
                    price_old = price_current
            text += '%s: %s, %s%%' %(name,price_current,change_percent)
            text += '\n'
            index += 1    
        if diff | True:
            Gtalk_send(text)
        else:
            print 'same ',
        time.sleep(15)
        
if  __name__ == '__main__':
    stock_daemon()        