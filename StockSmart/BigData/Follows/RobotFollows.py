import time
import sys
import os
import string
import subprocess
import thread 
import argparse
import socket
import urllib2, re

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')
active_cnt = 0
run_mode = 0

myip_checkinterval = 600 # check every 600s

def getmyip():
    try:
        url = urllib2.urlopen('http://ip138.com/ip2city.asp')
        result = url.read()
        m = re.search(r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])',result)
        return m.group(0)
    except:
        return 'Error'
        
def beep_sos(): 
    #sys.stdout.write('\a')
    print '\a'*2, 'beep !'

def external_cmd(cmd, msg_in=''):
    print cmd
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

def SendInfo_ReActive():
    global active_cnt
    active_cnt += 1
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    external_cmd("echo ReActived " + str(active_cnt) + " at " + text +" > body1.txt")
    external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()    

def Run_XQdailyFollowsChg():
    global run_mode
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    # external_cmd("echo Run_XQdailyFollowsChg at " + text +" > body1.txt")
    # external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()
    if run_mode == 1:
        stdout_value, stderr_value = external_cmd("XQdailyFollowsChg_6AM.bat")
    if run_mode == 2:
        stdout_value, stderr_value = external_cmd("XQdailyFollowsChg_8PM.bat")
    # print 'test XQdailyFollowsChg'
    # while True:
        # text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
        # print text
        # time.sleep(30)
    fp = open('external_cmd.log', 'wb')
    fp.write(stdout_value)
    fp.write(stderr_value)
    fp.close()
    beep_sos()
    beep_sos()
    
def DoCommand_CopyWatchListToCloud():
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    external_cmd("echo DoCommand_CopyWatchListToCloud at " + text +" > body1.txt")
    external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()
    external_cmd('pscp -batch -i myec2.ppk watch_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan')
    
     
    
def PowerState_Standby():
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    external_cmd("echo Sleep at " + text +" > body1.txt")
    external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()
    external_cmd('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    
def PowerState_Hibernate():
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    external_cmd("echo Hibernate at " + text +" > body1.txt")
    external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()
    external_cmd('rundll32.exe powrprof.dll,SetSuspendState')

def myip_changed_notification():
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    external_cmd("echo MyIP Changed at " + text +" > body1.txt")
    external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    
def Check_PrepareForOpen():
    global run_mode
    checkopen = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    if text >= '06:05' and text <= '06:07': 
        run_mode = 1
        checkopen = True
    if text >= '20:05' and text <= '20:07':
        run_mode = 2
        checkopen = True
    return checkopen
    
def Check_NeedWork():
    global run_mode
    checkopen = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    # print 'check', text
    if text >= '06:05' and text <= '06:07': 
        run_mode = 1
        checkopen = True

    # if text >= '10:10' and text <= '10:12': 
        # run_mode = 1
        # checkopen = True        
        
    if text >= '20:15' and text <= '20:17':
        run_mode = 2
        checkopen = True
    return checkopen

def Check_NeedSleep():   
    checkclose = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    # if text >= '07:20' and text <= '07:21': 
    # if text >= '00:10' and text <= '00:16': #TEST
        # checkclose = True
    # night
    if text >= '23:30' and text <= '23:31': 
        checkclose = True
    if text >= '10:15' and text <= '10:16': 
        checkclose = True
    if text >= '16:15' and text <= '16:16': 
        checkclose = True        
        
    return checkclose
    
if  __name__ == '__main__':
    force_sleep = False
    myip = ''
    myip_count = 0
    print 'Start !'
    SendInfo_ReActive()
    last_tick = time.time()    
    while True:
        print '.',
        time.sleep(60)
        curr_tick = time.time()
        elapsed = float('%.2f' %(curr_tick - last_tick))
        last_tick = curr_tick
        # print 'elapsed', elapsed
        if elapsed > 600:
            SendInfo_ReActive()
            continue

        if myip_count > (myip_checkinterval/30) or myip == '':
            newip = getmyip()
            if myip != newip and newip != 'Error':
                myip = newip
                myip_count = 0
                print 'New IP:', myip
                myip_changed_notification()
        else:
            myip_count += 1

        # Process Cmds
        if Check_NeedWork():
            print '\n*** Work for Money! ***'
            Run_XQdailyFollowsChg()
            last_tick = time.time()
            force_sleep = True
            continue
        # reset timer, Must before Sleep.
        # last_tick = time.time()
        if Check_NeedSleep() or force_sleep:
            print 'Sleep now.'
            if force_sleep:
                force_sleep = False
                time.sleep(60*10)
                DoCommand_CopyWatchListToCloud()
            PowerState_Hibernate()
            continue
    print 'Completed !'
    