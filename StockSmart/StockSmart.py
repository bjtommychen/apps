
#Used to get stock info.

import urllib2
import sys
import xml.etree.ElementTree as et

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
        strs = content.decode('gbk')
        data = strs.split('"')[1].split(',')
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
        strs = content.decode('gbk')
#        print 'tmp is %s\n' %(str.split('"')[0])
        data = strs.split('"')[1].split(',')
        name = "%-6s" % data[0]
        price_current = "%-6s" % float(data[3])
        change_percent = ( float(data[3]) - float(data[2]) )*100 / float(data[2])
        change_percent = "%s" % round (change_percent, 2)
        print 'name:',name,'curr:',price_current,'change',change_percent,'%'

def get_all_price(code_list):
    for code in code_list:
        get_price(code)

def get_K_char(code, len):
    url = 'http://chartapi.finance.yahoo.com/instrument/1.0/',code,'.ss/chartdata;type=quote;range=',len
    print url
    url = 'http://chartapi.finance.yahoo.com/instrument/1.0/%s.ss/chartdata;type=quote;range=1m' %code
    print url    
#    req = urllib2.Request(url)
#    strs = urllib2.urlopen(req).read()
#    strs = content.decode('gbk')
#    root = et.parse(filename).getroot()
    root = et.parse(urllib2.urlopen(url)).getroot()
    intro = root.find('values-meta').text.encode('gb2312')  
    print intro
    
WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?p=%s'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'

def weather_for_zip(zip_code):
    url = WEATHER_URL % zip_code
    rss = et.parse(urllib2.urlopen(url)).getroot()
    forecasts = []
    for element in rss.findall('channel/item/{%s}forecast' % WEATHER_NS):
        forecasts.append({
            'date': element.get('date'),
            'low': element.get('low'),
            'high': element.get('high'),
            'condition': element.get('text')
        })
    ycondition = rss.find('channel/item/{%s}condition' % WEATHER_NS)
    return {
        'current_condition': ycondition.get('text'),
        'current_temp': ycondition.get('temp'),
        'forecasts': forecasts,
        'title': rss.findtext('channel/title')
    }    
    
    
################################################################################
#test_google()
get_stockindex('s_sh000001')

#code_list = ['sh600036', 'sh600030']
#get_all_price(code_list)

get_K_char('600036', '1m')

