import os, sys, time
import string
import urllib, urllib2
import HTMLParser
import subprocess

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
        cmdline = 'phantomjs snap_webpage.js ' + url + ' capture.png > sinaweb.html'
        stdout_val, stderr_val = external_cmd(cmdline)
    fp = open('sinaweb.html', 'rb')
    data = fp.read()
    fp.close()
    # print 'crawler_geturl_phantomjs got bytes:', len(data)
    return data

class parseSinaWebFinanceText(HTMLParser.HTMLParser):
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
        if self.data[6][:pos].find('.') != -1:
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
    lParser = parseSinaWebFinanceText()
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
    
if  __name__ == '__main__':   
    # print get_hk_rt_price_SinaWeb_Requests('00393')
    print get_hk_rt_price_SinaWeb_Requests('08201')
    
    