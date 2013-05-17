
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


if  __name__ == '__main__':
    print 'This program is being run by itself'
#    test_StockSmart()

    text = ''
    for code in code_list:
        name, price_current, change_percent = get_price(code)
        text += '%s: %s, %s%%' %(name,price_current,change_percent)
        text += '\n'
#        text += name + price_current + change_percent
#    print text
    Gtalk_send(text)
    time.sleep(20)