﻿import os, sys, time
import string
import urllib, urllib2
import HTMLParser
import subprocess
import requests, re
import random

DebugMode = True #False

def write_data_to_file(data):
    fp = open('parsewebprice.html', 'wb')
    fp.write(data)
    fp.close()        

def read_data_from_file():
    fp = open('parsewebprice.html', 'rb')
    data = fp.read()
    fp.close()
    return data
        
def getIp(domain):
    import socket
    myaddr = socket.getaddrinfo(domain,'http')[0][4][0]
    return (myaddr)

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
    url = 'http://finance.qq.com/hk/q.htm?s=%s' % code
    if DebugMode:
        print url   
    data = crawler_geturl_phantomjs(url)
    data = data.decode('utf').encode('gbk')
    if DebugMode:
        write_data_to_file(data)    
        print 'get data', len(data)
    
    pos1 = data.find('<div class="titlebar"')
    pos2 = data.find('</span>', pos1)
    name_str = data[pos1:pos2+1]
    name_str = name_str[:name_str.rfind('</span>')]    
    name_str = name_str[name_str.rfind('>')+1:]  
    # print name_str
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
    name = code+name_str
    return (name, openprice, lastclose, curr, todayhigh, todaylow)
    
def get_hk_rt_price_QQWeb_Mobile(code):
    url = 'http://m.finance.qq.com/hk/q?f=HSI&sid=&s=%s' % code
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=2,headers=headers)
        data = r.content
        # print r.encoding, len(data)
        if False:
            write_data_to_file(data)
        r.close()
    except Exception, e:
        print 'Exception! when get', code, e
        return []
        
    pos1 = data.find('<div class="titlebar"')
    pos2 = data.find('</span>', pos1)
    name_str = data[pos1:pos2+1]
    name_str = name_str[:name_str.rfind('</strong>')]    
    name_str = name_str[name_str.rfind('>')+1:]
    name_str = name_str.decode('gbk')    
    # print name_str        
        
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
    name = code+name_str
    #time.sleep(1)
    return (name, openprice, lastclose, curr, todayhigh, todaylow)
    
ip_used_cnt = -1
ipaddress = ''
IP_STATIC_MAX = 1000    # Change IP every n times.    
# http://qt.gtimg.cn/r=0.13013921538367867q=r_hkHSI,r_hk08201,stdunixtime,r_hqingtime    
def get_hk_rt_price_gtimg(code):
    global ip_used_cnt
    global ipaddress
    ip_used_cnt += 1
    if ip_used_cnt > 1000 or ip_used_cnt == 0:
        ipaddress = getIp('qt.gtimg.cn')
        ip_used_cnt = 0
    # print 'Enter get_hk_rt_price_gtimg '
    random_seed = random.random()
    # print random_seed
    # url = 'http://qt.gtimg.cn/r=%sq=r_hk%s' % (random_seed, code)
    url = 'http://'+ipaddress+'/r=%sq=r_hk%s' % (random_seed, code)
    print url 
    try:
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
        data = content
    except Exception, e:
        return ('', 0, 0, 0, 0, 0)     
    
    # return
    # try:
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        # r = requests.get(url,timeout=2,headers=headers)
        # data = r.content
        # print r.encoding, len(data)
        # if False:
            # write_data_to_file(data)
        # r.close()
    # except Exception, e:
        # print 'Exception! when get', code, e
        # return []
    r = data.split('~')
    # print r
    # for i in range(0, len(r)):
        # print i, ':', r[i]
    curr = float(r[3])
    openprice = float(r[5])
    lastclose = float(r[4])
    todayhigh = float(r[33])
    todaylow = float(r[34])
    name_str = r[1]
    #print name_str, len(name_str)
    name_str = name_str.decode('gbk').encode('utf')
    name = code.encode('utf') + name_str
    # name = name.decode('gbk').encode('utf').decode('utf')
    # name = name.decode('gbk').encode('utf').decode('utf')
    return (name, openprice, lastclose, curr, todayhigh, todaylow)

    
def get_hk_rt_price(code):
    try:
    # return get_hk_rt_price_SinaWeb_Requests(code)
    # return get_hk_rt_price_QQWeb_Requests(code)
        one = get_hk_rt_price_gtimg(code)
        return one
    except:
        return ('', 0, 0, 0, 0, 0)
    
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
            data = data.strip().replace('\n', '')
            if (data.find('.') != -1 or data.isdigit()) and len(data) < 30:
                self.data.append(data)
                # print 'No.', self.idx, "Data     :", data
                self.idx += 1
    def MyProcess(self):
        print ''
        if self.data[0].find('.') != -1:
            self.price_curr = float(self.data[0])
        pos = self.data[1].find('(')
        if self.data[1][:pos].find('.') != -1:
            self.price_change = float(self.data[1][:pos])
        if self.data[3].find('.') != -1:                
            self.price_open = float(self.data[3])
    
def get_us_rt_price_SinaWeb_Requests(code):
    code = code.upper()
    url = 'http://stock.finance.sina.com.cn/usstock/quotes/%s.html?showhtml5' % code
    # print url
    data = crawler_geturl_phantomjs(url)
    # print 'get data', len(data)
    
    pos1 = data.find('<div class="hq_summary" id="hqSummary">')        
    pos2 = data.find('<th>贝塔系数', pos1)
    lParser = parseSinaWebFinanceText_usstock()
    lParser.feed(data[pos1:pos2])
    lParser.MyProcess()
    openprice = lParser.price_open
    curr = lParser.price_curr
    lastclose = curr - lParser.price_change
    lastclose = round(lastclose, 2)
    if lastclose < 0:
        lastclose = 0
    todayhigh = todaylow = 0    
    name = code
    return (name, openprice, lastclose, curr, todayhigh, todaylow)    
    
class parseGoogleFinanceText(HTMLParser.HTMLParser):
    def __init__(self):  
        HTMLParser.HTMLParser.__init__(self)  
        self.price_curr = 0.
        self.price_change = 0.
        self.price_open = 0.
        self.data=[]
    def handle_data(self, data):
        # print("Data     :", data)
        if data != '\n':
            self.data.append(string.replace(data,'\n',''))
    def MyProcess(self):
        try:
            self.price_curr = float(self.data[1])
            self.price_change = float(self.data[2])
            for i in range(0, len(self.data)):
                if self.data[i] == 'Open' and self.data[i+1][0].isdigit():
                    self.price_open = float(self.data[i+1])
                    break
        except:
            print '',
    # def handle_starttag(self, tag, attrs):
        # print("Start tag:", tag)
        # for attr in attrs:
            # print("     attr:", attr)
    # def handle_endtag(self, tag):
        # print("End tag  :", tag)
    # def handle_comment(self, data):
        # print("Comment  :", data)
    # def handle_entityref(self, name):
        # c = chr(name2codepoint[name])
        # print("Named ent:", c)
    # def handle_charref(self, name):
        # if name.startswith('x'):
            # c = chr(int(name[1:], 16))
        # else:
            # c = chr(int(name))
        # print("Num ent  :", c)
    # def handle_decl(self, data):
        # print("Decl     :", data)    
    
def get_us_rt_price_GoogleWeb_Requests(code):
    code = code.upper()
    url = 'http://www.google.com/finance?q=%s' % code
    # print url, '---------------------------------------------'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=15,headers=headers)
        data = r.content
        print r.encoding, len(data)
        if False:
            write_data_to_file(data)
        r.close()
    except Exception, e:
        return []   
    pos1 = data.find('span class="pr"')        
    pos2 = data.find('class="plusone-box"', pos1)
    # print pos1, pos2
    lParser = parseGoogleFinanceText()
    lParser.feed(data[pos1:pos2])
    # print lParser.data
    lParser.MyProcess()
    # print lParser.price_open, lParser.price_curr
    openprice = lParser.price_open
    curr = lParser.price_curr
    lastclose = curr - lParser.price_change
    todayhigh = todaylow = 0    
    name = code[:]
    # print 'GOOGLE Requests!',(name, openprice, lastclose, curr, todayhigh, todaylow)
    return (name, openprice, lastclose, curr, todayhigh, todaylow)    
    
# http://gp.3g.qq.com/g/s?aid=quote&securities_id=share_WBAI.xnys&stat=q_snyse&    
def get_us_rt_price_3gQQcom(code):
    code = code.upper()
    url = 'http://gp.3g.qq.com/g/s?aid=quote&securities_id=share_%s.xnas&stat=q_snasd&' % code
    print url
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=15,headers=headers)
        data = r.content
        print r.encoding, len(data)
        if False:
            write_data_to_file(data)
        r.close()
    except Exception, e:
        return []   
    match = re.compile(r'.*?\xe7\xbe\x8e\xe5\x85\x83')
    r = re.findall(match, data)
    # print len(r), r
    listv = []
    for one in r:
        pos1 = one.find(':')
        pos2 = one.find('\xbe\x8e\xe5\x85\x83')
        if pos1 != -1:
            # print one[pos1+1:pos2-1], len(one[pos1+1:pos2])
            listv.append(one[pos1+1:pos2-1])
    
    openprice = float(listv[3])
    curr = float(listv[0])
    lastclose = float(listv[2])
    todayhigh = float(listv[4])
    todaylow = float(listv[5])
    name = code[:]
    # print 'GOOGLE Requests!',(name, openprice, lastclose, curr, todayhigh, todaylow)
    return (name, openprice, lastclose, curr, todayhigh, todaylow)       
    
def get_us_rt_price(code):
    try:
        one = get_us_rt_price_GoogleWeb_Requests(code)
        #one = get_us_rt_price_SinaWeb_Requests(code)
    except:
        print 'get_us_rt_price except'
        return ('', 0,0,0,0,0)
    return one
    
if  __name__ == '__main__':   
    DebugMode = True
    # Test HK
    print 'Start Testing HK'
    print '(name, openprice, lastclose, curr, todayhigh, todaylow)'
    # print '?\n\r','get_hk_rt_price_QQWeb_Requests 00358,', get_hk_rt_price_QQWeb_Requests('00358')
    # print '?\n\r','get_hk_rt_price_QQWeb_Mobile 00358,', get_hk_rt_price_QQWeb_Mobile('00358')
    # print '?\n\r','get_hk_rt_price_SinaWeb_Requests 00358,', get_hk_rt_price_SinaWeb_Requests('00358')
    # print 'get_hk_rt_price_QQWeb_Requests 00224,', get_hk_rt_price_QQWeb_Requests('00224')
    # print 'get_hk_rt_price_QQWeb_Mobile 00224,', get_hk_rt_price_QQWeb_Mobile('00224')
    # print 'get_hk_rt_price_QQWeb_Requests 00218,', get_hk_rt_price_QQWeb_Requests('00218')
    # print 'get_hk_rt_price_QQWeb_Mobile 08201,', get_hk_rt_price_QQWeb_Mobile('08201')
    # print 'get_hk_rt_price_QQWeb_Requests 08201 ', get_hk_rt_price_QQWeb_Requests('08201')

    for i in range(0, 2):
        print get_hk_rt_price('00358')
        print get_hk_rt_price('00218')
        print get_hk_rt_price('08201')
    
    
    # Test US
    # print 'SinaWeb,',get_us_rt_price_SinaWeb_Requests('bidu')
    # print 'GoogleWeb,',get_us_rt_price_GoogleWeb_Requests('bidu')
    # print 'SinaWeb,',get_us_rt_price_SinaWeb_Requests('amcn')
    # print 'GoogleWeb,',get_us_rt_price_GoogleWeb_Requests('CO')
    print '3gQQcom, ', get_us_rt_price_3gQQcom('amcn')
    print 'GoogleWeb_Requests, ', get_us_rt_price_GoogleWeb_Requests('amcn')
    for i in range(0, 2):
        print get_us_rt_price('amcn')
        print get_us_rt_price('bidu')
        print get_us_rt_price('jmei')    
    