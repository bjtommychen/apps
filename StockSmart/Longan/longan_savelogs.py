 # -*- coding: utf-8 -*
import time
import sys
import os

print 'System Default Encoding:',sys.getdefaultencoding()

logs_filename = ''
logs_interval = 600
logs_strings = []
logs_stringslen = 0
logs_lastsavetime = 0

def get_DateString():
    return time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()) 
    
def SaveLogs_SetIntervalSeconds(seconds = 600):
    global logs_interval
    logs_interval = seconds
    
def SaveLogs_SaveOneString(string):
    global logs_strings
    global logs_filename
    global logs_interval
    global logs_lastsavetime
    global logs_stringslen
    
    if len(string) < 1:
        return
    if logs_filename == '':
        logs_filename = 'logs/Logs-'+get_DateString()+'.txt'
        print 'LOGS: logs_filename', logs_filename
    logs_strings.append(string)
    logs_stringslen += len(string)
    print 'logs_strings len:', logs_stringslen
    if logs_lastsavetime != 0 and (time.time() - logs_lastsavetime) > logs_interval and logs_stringslen > 20000:
        fp = open(logs_filename, 'wb')
        fp.writelines(logs_strings)
        fp.close()
        print 'LOGS: Saved to file', logs_filename
        logs_strings = []
        logs_filename = ''
        logs_stringslen = 0
    logs_lastsavetime = time.time()
    
def SaveLogs_Flush():
    global logs_strings
    global logs_filename
    global logs_stringslen
    
    if logs_filename == '':
        logs_filename = 'logs/Logs-'+get_DateString()+'.txt'
        print 'LOGS: logs_filename', logs_filename
    if logs_strings != []:        
        fp = open(logs_filename, 'wb')
        fp.writelines(logs_strings)
        fp.close()
        print 'LOGS: Saved to file', logs_filename
    logs_strings = []
    logs_filename = ''
    logs_stringslen = 0
    
#######################################################################    
if  __name__ == '__main__':
    print '#'*60
    print '##### Longan System. by Tommy ' 
    print '#'*60
    print 'Config:'
    
    SaveLogs_SetIntervalSeconds(10)
    SaveLogs_SaveOneString("string 1")
    time.sleep(1)
    SaveLogs_SaveOneString("string 11\n")
    SaveLogs_SaveOneString("string 12\n")
    SaveLogs_SaveOneString("string 13\n")
    time.sleep(15)
    SaveLogs_SaveOneString("string 14\n")
    SaveLogs_SaveOneString("string 15\n")
    time.sleep(15)
    SaveLogs_SaveOneString("string 16\n")
    SaveLogs_SaveOneString("string 17\n")
    SaveLogs_SaveOneString("string 18\n")
    time.sleep(15)
    
    print 'Done.'