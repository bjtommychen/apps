import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import struct
import workerpool
import threading
import profile
import subprocess
# import psyco
# 
# psyco.full()

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
# sys.setdefaultencoding('utf8')
sys.setdefaultencoding('gbk')

data_path = "output/"
data_ext="csv"
bUseMultiCore = True
thread_num=4
threads = []

def external_cmd(cmd, msg_in=''):
#     print cmd
#     return None, None
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
#            print fullname
            st = os.lstat(fullname)
            if stat.S_ISDIR(st.st_mode) and subdir:
                dirlist += getFileList(fullname,ext)
            elif os.path.isfile(fullname):
                if fnmatch.fnmatch( fullname, ext): 
                    dirlist.append(fullname)
                else:
                    pass
        return dirlist
    else:
        return [] 
    

def Get_AllSpurtData():
    dirlist = getFileList(data_path, '*.'+data_ext, subdir = False)
    listall = []
    i = 0
    total = len(dirlist)
    if bUseMultiCore == False:
        for filename in dirlist:
            i+=1
            print 'No.', i, '/', total, ', Checking...', filename
            Get_OneSpurtData(filename)
#             csvWriter.writerow(line)
    else:
        Do_MultiThread(dirlist)
    
def Get_OneDayData(lines, index):
    daylines = []
    i = index
    count = 0
    while (i < len(lines)):
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = lines[i]
        m_time = int(m_time)
        m_fOpen = float(m_fOpen)
        m_fHigh = float(m_fHigh)
        m_fLow = float(m_fLow)
        m_fClose = float(m_fClose)
        m_fVolume = int(m_fVolume)
        m_fAmount = int(m_fAmount)
        wline = time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount
        daylines.append(wline)
        count += 1
        i += 1
        if (count >= 240) or time_str.find('15:00:00') != -1:
            break;
    index = i
#     print 'index', index
    return index, daylines
    
def Get_OneSpurtData_byCmd(filename):
    cmdline = 'pypy ' +'GetSpurtData_One.py ' + filename
#     print cmdline    
    stdout_val, stderr_val = external_cmd(cmdline)
#     print stdout_val
    line = stdout_val.strip()
    return line
    
def Get_OneSpurtData(filename):
    reader = csv.reader(file(filename,'rb'))
    alllines = []
    m_fLastClose = 0.0    
    for row in reader:
        alllines.append(row)
    print 'line', len(alllines)
    code,name,cnt = alllines[0]    
    cnt_days=0
    cnt_boom=0
    cnt_boom_failed=0
    index = 1   # skip 1st line.
    while(True):
        index, daylines = Get_OneDayData(alllines, index)
        if (daylines == []):
            break;
        cnt_days += 1
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        #init last close
        if m_fLastClose == 0.0:
            m_fLastClose = m_fClose
            continue
#         print 'Checking ', time_str
        #chec Boom
        max_price = m_fLastClose *1.095
        bHit = False
        for i in xrange(0, len(daylines)):
            time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[i]
            if m_fHigh > max_price and bHit == False:
#                 print "Boom! at", time_str, m_fLastClose, m_fHigh, i
                bHit = True
                cnt_boom += 1
                break
        time_str, m_time, m_fOpen, m_fHigh, m_fLow, m_fClose, m_fVolume, m_fAmount = daylines[len(daylines)-1]
        m_fLastClose = m_fClose
        if bHit ==True:
            if (m_fClose < max_price):
#                 print "Boom Failed !" ,m_fClose ,max_price
                cnt_boom_failed += 1
#     print cnt_days, cnt_boom, cnt_boom_failed, float('%.2f' % (float(cnt_boom)*100/cnt_days)), '%', float('%.2f' % (float(cnt_boom_failed)*100/cnt_boom)), '%'
    if cnt_days == 0:
        cnt_days = 1
    if cnt_boom == 0:
        cnt_boom = 1               
    line = code, name, cnt_days, cnt_boom, cnt_boom_failed , float('%.2f' % (float(cnt_boom)*100/cnt_days)), float('%.2f' % (float(cnt_boom_failed)*100/cnt_boom))
    print line
#     return line
    csvWriter.writerow(line)                

class DoOneThread (threading.Thread): 
    def __init__(self, filename, taskid):
        threading.Thread.__init__(self)
        self.filename = filename
        self.taskid = taskid
    def run(self):                   
        print "Starting " , self.taskid     #self.name
        Get_OneSpurtData(self.filename)
        print "Exiting " , self.taskid     #self.name
        time.sleep(0.1)
        
class DoOneJob(workerpool.Job):
    "Job for downloading a given URL."
    def __init__(self, filename, taskid):
        self.filename = filename
        self.taskid = taskid
    def run(self):
        try:  
            if False:
                thread1 = DoOneThread(self.filename, self.taskid)
                thread1.start()
                thread1.join(timeout=100)
            else:
                str_lines = Get_OneSpurtData_byCmd(self.filename)
                print str_lines
                lines = str_lines.split('\r\n')
                for line in lines:
                    line = line.split()
                    csvWriter.writerow(line)
            print 'Job', self.taskid, 'done!'
            time.sleep(0.1)
        except:
            print 'DoOneJob failed.'

def Do_MultiThread(dirlist):
    global thread_num
    # Initialize a pool, 5 threads in this case
    pool = workerpool.WorkerPool(size=thread_num, maxjobs=thread_num)
    cnt = 0
    runcnt = 0
    total = len(dirlist)
    for filename in dirlist:
#         thread.start_new_thread(Get_OneSpurtData,(filename,))
#         print 'thread start '
        try:
            try:
                job = DoOneJob(filename, runcnt)
                print 'Job', runcnt, '/', total
                pool.put(job)    
                runcnt += 1
                time.sleep(0.5)
            except:
                print 'get  error'
                break
        except:
            break
    # Send shutdown jobs to all threads, and wait until all the jobs have been completed
#     time.sleep(10)
    pool.shutdown()
    pool.wait()


        
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Spurt Data from csv files.'
    print '#'*60
    print 'Config:'
    print '\tdata_path =', data_path
    print '\tdata_ext =', data_ext
    print '\tbUseMultiCore = ', bUseMultiCore
    print '\tthread_num = ', thread_num
        
    if len(sys.argv) > 1:
        exit(0)
    print '\n\nWait 2s to start ... Ctrl+C to cancle now !\n'
    time.sleep(2)    
    print 'Start !'
    start = time.time()
    fcsv = open("get_all_data.csv", 'wb')
    csvWriter = csv.writer(fcsv)    
    Get_AllSpurtData()
#     profile.run("Get_AllSpurtData()")
    fcsv.close()    
    end = time.time()
    elapsed = float('%.2f' %(end - start))
    print "Time taken: ", elapsed, "seconds."
    print 'Completed !'
    