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
    text = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    external_cmd("echo Run_XQdailyFollowsChg at " + text +" > body1.txt")
    # external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()
    external_cmd("XQdailyFollowsChg.bat")
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
    # external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()
    external_cmd('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    
def Check_NeedWork():
    checkopen = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    print 'check', text
    if text >= '06:16' and text <= '06:18': 
        checkopen = True
    # if text >= '08:47' and text <= '08:59': #TEST    
        # checkopen = True
    return checkopen

def Check_NeedSleep():   
    checkopen = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    if text >= '07:00' and text <= '07:02': 
    # if text >= '00:10' and text <= '00:16': #TEST
        checkopen = True
    return checkopen
    
if  __name__ == '__main__':
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
        if Check_NeedSleep():
            print 'Sleep now.'
            PowerState_Standby()
        if Check_NeedWork():
            print 'Work for Money!'
            Run_XQdailyFollowsChg()
        # reset timer
        start = time.time()
    print 'Completed !'
    