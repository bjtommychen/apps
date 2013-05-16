
from StockSmart import *

code_list = ['sh600036', 'sh600030']

print 'System Default Encoding:',sys.getdefaultencoding()

def test_StockSmart():
    test_google()
    test_sina()
    get_stockindex('s_sh000001')
    get_all_price(code_list)
    get_K_char('600036', '1m')


test_StockSmart()