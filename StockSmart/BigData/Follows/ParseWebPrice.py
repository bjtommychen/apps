import os, sys, time
import string
import urllib, urllib2
import HTMLParser
import subprocess
import requests, re

debugmode = True

def external_cmd(cmd, msg_in=''):
#    print cmd
#     return None, None
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        time.sleep(0.2)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None    
    

def crawler_geturl_phantomjs(url):
    # print url
    if True:
        cmdline = 'phantomjs snap_webpage.js ' + url + ' capture.png > parsewebprice.html'
        stdout_val, stderr_val = external_cmd(cmdline)
    fp = open('parsewebprice.html', 'rb')
    data = fp.read()
    fp.close()
    # print 'crawler_geturl_phantomjs got bytes:', len(data)
    return data

class parseSinaWebFinanceText_hkstock(HTMLParser.HTMLParser):
    def __init__(self):  
        HTMLParser.HTMLParser.__init__(self)  
        self.price_curr = 0.
        self.price_change = 0.
        self.price_open = 0.
        self.data=[]
        self.idx = 0
    def handle_data(self, data):
        if data != '\n':
            self.data.append(string.replace(data,'\n',''))
            # print self.idx, "Data     :", data
            self.idx += 1
    def MyProcess(self):
        # print self.data[1],  type(self.data[1]), self.data[1][0].isdigit(), self.data[1].find('.')
        # print self.data
        if self.data[1].find('.') != -1:
            self.price_curr = float(self.data[1])
        pos = self.data[6].find('（')
        if pos == -1:
            pos = self.data[6].find('(')
        if self.data[6][:pos].find('.') != -1 and self.data[6][:pos].find('--') == -1:
            # print self.data[6][:pos], float(self.data[6][:pos])
            self.price_change = float(self.data[6][:pos])
        if self.data[85].find('.') != -1:                
            self.price_open = float(self.data[85])
        # for i in range(0, len(self.data)):
            # if self.data[i] == 'Open' and self.data[i+1].isdigit():
                # self.price_open = float(self.data[i+1])
                # break    

def get_hk_rt_price_SinaWeb_Requests(code):
    code = code.upper()
    url = 'http://stock.finance.sina.com.cn/hkstock/quotes/%s.html' % code
    # print url
    data = crawler_geturl_phantomjs(url)
    # print 'get data', len(data)
    
    pos1 = data.find('class="deta01 clearfix')        
    pos2 = data.find('class="deta04 auction', pos1)
    lParser = parseSinaWebFinanceText_hkstock()
    lParser.feed(data[pos1:pos2])
    # print lParser.data
    lParser.MyProcess()
    # print lParser.price_open, lParser.price_curr
    openprice = lParser.price_open
    curr = lParser.price_curr
    lastclose = curr - lParser.price_change
    if lastclose < 0:
        lastclose = 0
    # print lParser.price_open, lParser.price_curr, lParser.price_change
    todayhigh = todaylow = 0    
    name = code
    # print 'SinaWeb Requests!',(name, openprice, lastclose, curr, todayhigh, todaylow)
    # print 'SinaWeb',
    return (name, openprice, lastclose, curr, todayhigh, todaylow)
    
class parseQQWebFinanceText_hkstock(HTMLParser.HTMLParser):
    def __init__(self):  
        HTMLParser.HTMLParser.__init__(self)  
        self.price_curr = 0.
        self.price_change = 0.
        self.price_open = 0.
        self.data=[]
        self.idx = 0
    def handle_data(self, data):
        if data != '\n':
            self.data.append(string.replace(data,'\n',''))
            # print self.idx, "Data     :", len(data), 'data:', data
            self.idx += 1
    def MyProcess(self):
        if self.data[4].find('.') != -1:
            self.price_curr = float(self.data[4])
        if self.data[12].find('.') != -1:
            self.price_change = float(self.data[12])
        if self.data[30].find('.') != -1:                
            self.price_open = float(self.data[30])
        # for i in range(0, len(self.data)):
            # if self.data[i] == 'Open' and self.data[i+1].isdigit():
                # self.price_open = float(self.data[i+1])
                # break        
    
def get_hk_rt_price_QQWeb_Requests(code):
    url = 'http://finance.qq.com/hk/q.htm?stockcode=%s' % code
    # print url
    data = crawler_geturl_phantomjs(url)
    # print 'get data', len(data)
    
    pos1 = data.find('<div class="price">')        
    pos2 = data.find('<div class="part2">', pos1)
    lParser = parseQQWebFinanceText_hkstock()
    lParser.feed(data[pos1:pos2])
    # print lParser.data
    lParser.MyProcess()
    # print lParser.price_open, lParser.price_curr
    openprice = lParser.price_open
    curr = lParser.price_curr
    lastclose = curr - lParser.price_change
    if lastclose < 0:
        lastclose = 0
    # print lParser.price_open, lParser.price_curr, lParser.price_change
    todayhigh = todaylow = 0    
    name = code
    return (name, openprice, lastclose, curr, todayhigh, todaylow)
    
def get_hk_rt_price_QQWeb_Mobile(code):
    url = 'http://m.finance.qq.com/hk/q?f=HSI&sid=&s=%s' % code
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        data = r.content
        # print r.encoding, len(data)
        if True:
            fp = open('parsewebprice.html', 'wb')
            fp.write(data)
            fp.close()        
        r.close()
    except Exception, e:
        print 'Exception!'
        return []
        
    pos1 = data.find('<div class="price">')        
    pos2 = data.find('<div class="part2">', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return []
    data = data[pos1:pos2]    
    match = re.compile(r'(?<=>).*?(?=<)')
    r = re.findall(match, data)
    # print len(r), r
    # for i in range(0, len(r)):
        # print i, r[i]
    curr = float(r[1])
    openprice = float(r[27])
    lastclose = float(r[29])
    todayhigh = todaylow = 0
    name = code
    return (name, openprice, lastclose, curr, todayhigh, todaylow)
    
    
def get_hk_rt_price(code):
    # return get_hk_rt_price_SinaWeb_Requests(code)
    # return get_hk_rt_price_QQWeb_Requests(code)
    return get_hk_rt_price_QQWeb_Mobile(code)
    
###################### US ############################    
class parseSinaWebFinanceText_usstock(HTMLParser.HTMLParser):
    def __init__(self):  
        HTMLParser.HTMLParser.__init__(self)  
        self.price_curr = 0.
        self.price_change = 0.
        self.price_open = 0.
        self.data=[]
        self.idx = 0
    def handle_data(self, data):
        if data != '\n':
            self.data.append(string.replace(data,'\n',''))
            # print 'No.', self.idx, "Data     :", data
            self.idx += 1
    def MyProcess(self):
        if self.data[1].find('.') != -1:
            self.price_curr = float(self.data[1])
        pos = self.data[5].find('(')
        if self.data[5][:pos].find('.') != -1:
            self.price_change = float(self.data[5][:pos])
        if self.data[64].find('.') != -1:                
            self.price_open = float(self.data[64])
    
def get_us_rt_price_SinaWeb_Requests(code):
    code = code.upper()
    url = 'http://stock.finance.sina.com.cn/usstock/quotes/%s.html?showhtml5' % code
    # print url
    data = crawler_geturl_phantomjs(url)
    # print 'get data', len(data)
    
    pos1 = data.find('<div class="hq_summary" id="hqSummary">')        
    pos2 = data.find('<th>前收盘', pos1)
    lParser = parseSinaWebFinanceText_usstock()
    lParser.feed(data[pos1:pos2])
    lParser.MyProcess()
    openprice = lParser.price_open
    curr = lParser.price_curr
    lastclose = curr - lParser.price_change
    if lastclose < 0:
        lastclose = 0
    todayhigh = todaylow = 0    
    name = code
    return (name, openprice, lastclose, curr, todayhigh, todaylow)    
    
def get_us_rt_price_GoogleWeb_Requests(code):
    code = code.upper()
    url = 'http://www.google.com/finance?q=%s' % code
    print url, '---------------------------------------------'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=15,headers=headers)
        data = r.content
        # print r.encoding
        r.close()
    except Exception, e:
        return []   
    pos1 = data.find('span class="pr"')        
    pos2 = data.find('class="plusone-box"', pos1)
    lParser = parseGoogleFinanceText()
    lParser.feed(data[pos1:pos2])
    # print lParser.data
    lParser.MyProcess()
    # print lParser.price_open, lParser.price_curr
    openprice = lParser.price_open
    curr = lParser.price_curr
    lastclose = curr - lParser.price_change
    todayhigh = todaylow = 0    
    name = code
    print 'GOOGLE Requests!',(name, openprice, lastclose, curr, todayhigh, todaylow)
    return (name, openprice, lastclose, curr, todayhigh, todaylow)    
    
def get_us_rt_price(code):
    return get_us_rt_price_GoogleWeb_Requests(code)
    # return get_us_rt_price_SinaWeb_Requests(code)
    
if  __name__ == '__main__':   
    print 'qq web fast version 00358,', get_hk_rt_price_QQWeb_Requests('00358')
    print 'qq, web mobile version 00358,', get_hk_rt_price_QQWeb_Mobile('00358')
    # print 'sina web 00358,', get_hk_rt_price_SinaWeb_Requests('00358')
    # print 'qq, web mobile version ', get_hk_rt_price_QQWeb_Requests('08201')
    print 'SinaWeb,',get_us_rt_price_SinaWeb_Requests('bidu')
    print 'GoogleWeb,',get_us_rt_price_SinaWeb_Requests('bidu')
    print 'SinaWeb,',get_us_rt_price_SinaWeb_Requests('amcn')
    print 'GoogleWeb,',get_us_rt_price_SinaWeb_Requests('amcn')
    
    