import time
import sys
import os
import string
import subprocess
import thread 
import argparse

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
sys.setdefaultencoding('utf')
active_cnt = 0

run_mode = 0

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
        external_cmd("XQdailyFollowsChg_6AM.bat")
    if run_mode == 2:
        external_cmd("XQdailyFollowsChg_8PM.bat")
    # print 'test XQdailyFollowsChg'
    # while True:
        # text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
        # print text
        # time.sleep(30)
    beep_sos()
    beep_sos()
    
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
    if text >= '20:05' and text <= '20:07':
        run_mode = 2
        checkopen = True
    return checkopen

def Check_NeedSleep():   
    checkclose = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    if text >= '07:20' and text <= '07:30': 
    # if text >= '00:10' and text <= '00:16': #TEST
        checkclose = True
    # night
    if text >= '21:00' and text <= '21:01': 
        checkclose = True

    if text >= '10:15' and text <= '10:20': 
        checkclose = True
    if text >= '16:15' and text <= '16:20': 
        checkclose = True        
        
    return checkclose
    
if  __name__ == '__main__':
    force_sleep = False
    print 'Start !'
    SendInfo_ReActive()
    start = time.time()    
    while True:
        print '.',
        time.sleep(30)
        end = time.time()
        elapsed = float('%.2f' %(end - start))
        # print 'elapsed', elapsed
        if elapsed > 40:
            SendInfo_ReActive()
        # Process Cmds
        if Check_NeedWork():
            print '\n*** Work for Money! ***'
            Run_XQdailyFollowsChg()
            force_sleep = True
        # reset timer, Must before Sleep.
        start = time.time()
        if Check_NeedSleep() or force_sleep:
            print 'Sleep now.'
            force_sleep = False
            PowerState_Hibernate()
    print 'Completed !'
    