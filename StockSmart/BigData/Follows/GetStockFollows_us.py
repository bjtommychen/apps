import time
import sys
import os
import socket
import math
import csv
import urllib2
import urllib
import string
import re
import csv
import requests
import time
import subprocess

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')

DebugMode = False

def external_cmd(cmd, rundir='./', msg_in=''):
    # print 'rundir:',rundir, ', cmds:', cmd
    # return 'stdout', 'stderr'
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   cwd=rundir
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        # time.sleep(0.2)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None


def convert_num(string):
    return str(string)

def getmyip():
    try:
        url = urllib2.urlopen('http://ip138.com/ip2city.asp')
        result = url.read()
        # m = re.search(r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])',result)
        m = re.search(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)',result) #TOMMY
        return m.group(0)
    except:
        return ''    
		
def get_StockFollows(code):
    url = 'http://xueqiu.com/S/%s/follows' % code
    # print url
    # return []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        r = requests.get(url,timeout=5,headers=headers)
        if not r.ok:
            if r.status_code == 404:
                return ['404', '404', '404']
            print r.status_code
        data = r.content
        if data.find('captcha') != -1:
            return ['captcha', 'captcha', 'captcha']
        # print r.encoding
        r.close()
    except Exception, e:
        print 'Exception!', code
        return []

    pos1 = data.find('div class="stockInfo"')        
    pos2 = data.find('div class="follower-list"', pos1)  
    # print pos1, pos2
    if pos1 == -1 and pos2 == -1:
        return []
    data = data[pos1:pos2]    
    match = re.compile(r'(?<=a href=).*?(?=<\/a>)')
    r_name = re.findall(match, data.encode('gbk'))
    pos1 = r_name[0].find('>') 
    pos2 = r_name[0].find('(', pos1) 
    name = r_name[0][pos1+1:pos2]
    codename = r_name[0][pos2:]
    match = re.compile(r'(?<=<span>).*?(?=<\/span>)')
    r = re.findall(match, data.encode('gbk'))
    # print len(r), r
    pos1 = r[0].find('(')        
    pos2 = r[0].find(')', pos1)      
    if pos1 == -1 and pos2 == -1:
        return []
    return (name, codename, r[0][pos1+1:pos2])
        
followlist = []    
def write_follows_csv(csvfilename, flist):    
    fcsv = open(csvfilename, 'wb')
    csvWriter = csv.writer(fcsv)
    titles = 'Name', '代码', '粉丝数'
    title = []
    for one in titles:
        title.append(one.encode('gbk'))
    csvWriter.writerow(title)
    for one in flist:
        csvWriter.writerow(one)
    fcsv.close()  
    
def get_stock_follows(currlist = []):
    global DebugMode
    if os.environ.get('TOMMYDEBUG') == 'True':
        DebugMode = True
    initmode = False
    outlist = []
    if currlist == []:
        initmode = True
    else:
        outlist = currlist[:]
    count = 0
    total = 0
    falsecnt = 0
    if True: # from list
        reader = csv.reader(file('stocklist_us.csv','rb')) 
        print 'Got list from csv'
        for one in reader:   
            total += 1
            code, name = one
            if initmode == False:
                first_or_default = next((x for x in outlist if x[1].find(code)!=-1), None)
                if first_or_default != None:
                    # print 'skip', code
                    continue
                # else:
                    # print 'need read', code, count
                    # count += 1
                    # continue
            # print code, name
            codestr = code
            if (count%100 == 0):
                print codestr
                time.sleep(.1)
            infostr = get_StockFollows(codestr)
            if len(infostr) > 0:
                if infostr[0] == '404':
                    print '',
                elif infostr[0] == 'captcha':
                    print 'FOUND CAPTCHA! pppoe_restart ... ',
                    external_cmd('pppoe_restart.bat')
                    time.sleep(5)
                    print 'DONE.'
                else:
                    count += 1
                    outlist.append(infostr)
                    if initmode == False:
                        print '#'*5, infostr
            else:
                # when error, delay more.
                falsecnt += 1
                if (falsecnt % 5 == 0):
                    while True:
                        if getmyip() != '':
                            break
                        time.sleep(30)
                        print 'wait for online ...'
                time.sleep(.1)   #count%10+5)
            
            print '.'*(count%10+3)+'^'+'.'*(10-count%10+3)+str(count)+'/'+str(total), '\r',
            if DebugMode and total > 100:
                break                
    return outlist                    

def get_us_list():
    f = open('us_cn.txt', "r")
    list1 = f.readlines()
    f.close()
    f = open('us_hot.txt', "r")
    list2 = f.readlines()
    f.close()
    print 'read in', len(list1), len(list2)
    list1 += list2
    rlist = []
    for line in list1:
        data=line.split()
        if len(data) > 2 and data[0].isalpha():
            wline = data[0], data[1]
            rlist.append(wline)
    # print rlist, len(rlist)
    print 'return list', len(rlist)
    return rlist
 
if  __name__ == '__main__':
    print 'Start !'
    print get_StockFollows('AMCN')
    timetext = time.strftime("%Y-%m-%d-%H-%M", time.localtime()) 
    csvfilename = 'data/nasdaq-'+timetext+'.csv'  
    print 'csvfilename', csvfilename 
    followlist = []
    if False:
        reader = csv.reader(file('./data/nasdaq-2015-03-12-06-05.csv','rb')) 
        for one in reader:
            followlist.append(one)
    print 'followlist',len(followlist)
    time1st = True
    while True:
        time.sleep(1)
        followlist = get_stock_follows(followlist)
        print 'followlist',len(followlist)
        write_follows_csv(csvfilename, followlist)
        if len(followlist) > 500 and time1st == False:
            time.sleep(6)
            break
        time1st = False
        print 'one loop done.'
        time.sleep(60)
    print 'Completed !'
    