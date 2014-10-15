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

def beep_sos(): 
    #sys.stdout.write('\a')
    print '\a'*2

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
    external_cmd("echo ReActived. > body1.txt")
    external_cmd("xq_follows_sendmail.py Robot_News@xueqiu# body1.txt")
    beep_sos()    

def Run_XQdailyFollowsChg():
    beep_sos()
    external_cmd("XQdailyFollowsChg.bat")
    beep_sos()
    
def PowerState_Standby():
    beep_sos()
    external_cmd('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    
def Check_NeedWork():
    checkopen = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    if text >= '06:30' and text <= '06:31': 
    # if text >= '00:07' and text <= '00:08': #TEST    
        checkopen = True
    return checkopen

def Check_NeedSleep():   
    checkopen = False
    # if (datetime.datetime.now().weekday() > 4):
        # return False
    text = time.strftime("%H:%M", time.localtime())
    # print text
    if text >= '07:30' and text <= '07:31': 
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
            PowerState_Standby()
        if Check_NeedWork():
            Run_XQdailyFollowsChg()
        # reset timer
        start = time.time()
    print 'Completed !'
    