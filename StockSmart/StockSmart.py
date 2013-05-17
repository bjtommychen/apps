
#Used to get stock info.
import os
import urllib2
import urllib
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


percent_start = 0
def test_sina_callback(a, b, c):  
    global percent_start
    per = 100.0 * a * b / c  
    if per > 100:  
        per = 100 
    if (per >= percent_start) :
        print '%.2f%%,' % per,
        percent_start += 10  

def test_sina():  
    print '\n*** Test Sina ***'
    url = 'http://www.sina.com.cn'  
    local = 'sina.html'  
    urllib.urlretrieve(url, local, test_sina_callback)
    print '\nSina home page html size', os.path.getsize(local), 'bytes!'

def test_google():
    print '\n*** Test Google ***'
    google = urllib2.urlopen('http://hq.sinajs.cn/?list=s_sh000001')  
    print 'http header:\n', google.info()  
    print 'http status:\n', google.getcode()  
    print 'url:', google.geturl()  
    for line in google: 
        print line,  
    google.close()  


def get_stockindex(code):
    if(len(code)) == 0:
        return
    url = 'http://hq.sinajs.cn/?list=%s' % code
    req = urllib2.Request(url)
    content = urllib2.urlopen(req).read()
    strs = content.decode('gbk')
    data = strs.split('"')[1].split(',')
    name = "%s" % data[0]
    price_current = "%-6s" % float(data[1])
    change_percent = "%s" % float(data[3])
    print 'name:%s, curr:%s, change:%s%%' %(name,price_current,change_percent)
        
def get_price(code):
    url = 'http://hq.sinajs.cn/?list=%s' % code
    req = urllib2.Request(url)
#        req.set_proxy('proxy.XXX.com:911', 'http')
    content = urllib2.urlopen(req).read()
    strs = content.decode('gbk')
    data = strs.split('"')[1].split(',')
    name = "%s" % data[0]
    price_current = "%-5s" % float(data[3])
    change_percent = ( float(data[3]) - float(data[2]) )*100 / float(data[2])
    change_percent = "%s" % round (change_percent, 2)
    return (name, price_current,change_percent)

def get_all_price(code_list):
    print '\n*** Test get_all_price ***'
    for code in code_list:
        name, price_current, change_percent = get_price(code)
    print 'name:%s, curr:%s, change:%s%%' %(name,price_current,change_percent)

def get_K_char(code, len):
    print '\n*** Test get_K_char ***'
    url = 'http://chartapi.finance.yahoo.com/instrument/1.0/%s.ss/chartdata;type=quote;range=%s' %(code,len)
    print url    
    data=urllib2.urlopen(url).read()
#    print data
#    tree = ET.ElementTree(file='doc1.xml')
#    root = tree.getroot()
    root = ET.fromstring(data)
    print root.tag, root.attrib

    for i in range(0, 5, 1):
        print root[1][i].tag, root[1][i].attrib
            
    for child in root:
        print child.tag, child.attrib

    for child in root.findall('reference-meta'):
        min_value = child.find('min').text
        max_value = child.find('max').text
        print min_value, max_value

    for daydata in root.iter('p'):
        print 'Date', daydata.attrib.get('ref'),
        if (float(daydata[4].text) != 0):
            for i in range(5):
                meta = root[1][i].attrib.get('id')
                print meta,':',
                price = float(daydata[i].text)
                print "%.2f," %price,
        else:
            print 'CLOSE!',
        print

    
################################################################################


