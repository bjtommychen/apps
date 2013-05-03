
#Used to get stock info.

import urllib2
import sys

print 'System Default Encoding:',sys.getdefaultencoding()

def test_google():
    google = urllib2.urlopen('http://hq.sinajs.cn/?list=s_sh000001')  
    print 'http header:\n', google.info()  
    print 'http status:\n', google.getcode()  
    print 'url:', google.geturl()  
    for line in google: 
        print line,  
    google.close()  

def get_stockindex(code):
        url = 'http://hq.sinajs.cn/?list=%s' % code
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
        str = content.decode('gbk')
        data = str.split('"')[1].split(',')
        name = "%-6s" % data[0]
        price_current = "%-6s" % float(data[1])
        change_percent = "%s" % float(data[3])
        print 'name:',name,'curr:',price_current,'change',change_percent,'%'

def get_price(code):
        url = 'http://hq.sinajs.cn/?list=%s' % code
        req = urllib2.Request(url)
#        req.set_proxy('proxy.XXX.com:911', 'http')
        content = urllib2.urlopen(req).read()
#        print 'content is %s' %content
        str = content.decode('gbk')
#        print 'tmp is %s\n' %(str.split('"')[0])
        data = str.split('"')[1].split(',')
        name = "%-6s" % data[0]
        price_current = "%-6s" % float(data[3])
        change_percent = ( float(data[3]) - float(data[2]) )*100 / float(data[2])
        change_percent = "%s" % round (change_percent, 2)
        print 'name:',name,'curr:',price_current,'change',change_percent,'%'

def get_all_price(code_list):
    for code in code_list:
        get_price(code)

#test_google()
get_stockindex('s_sh000001')

code_list = ['sh600036', 'sh600030']
get_all_price(code_list)
