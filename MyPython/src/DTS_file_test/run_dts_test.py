import time
import sys
import os
import string
import subprocess
import thread 
import workerpool

srcdir='D:'
dstdir='M:\\'
# dstdir='D:\\DTS_TMP_DIR\\'
cygwin_dir='c:\\cygwin\\bin\\'
bRemvoeFileAfterCheck = True

thread_num=10

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

def run_cmdline(line):
#     print line
    line = line.strip()
    line = line.replace('filename=', 'filename='+srcdir)
    line = line.replace('outputdir=D:\\DTS\\M8\\dts_test\\M8\\', 'outputdir='+dstdir )    
    
    cmds = line.split()
#     print len(cmds)
    if len(cmds) < 3:
        print 'parameter count < 3, error!'
        return

##### Do decode #####    
#     if cmds[0].find('dts_decoder_dut') != -1:
#         return
    
#     for i in range(0, len(cmds)):
#         print i, cmds[i]
#     print '--'

    if cmds[0].find('dts_decoder_dut') != -1:
        dir2mk = ''
        for i in range(1, len(cmds)):
            if cmds[i].find('outputdir') != -1:
                idx = cmds[i].find(dstdir)
                dir2mk= cmds[i][idx:]
                
#         print dir2mk
        cmdline = cygwin_dir +'mkdir --parents ' + dir2mk
#         print cmdline
        stdout_val, stderr_val = external_cmd(cmdline)
#         print 'Standard Output: %s' % stdout_val
#         print 'Standard Error: %s' % stderr_val
        
        line =  " ".join(cmds)
#         print line        
        stdout_val, stderr_val = external_cmd(line)
#         print 'Standard Output: %s' % stdout_val
#         print 'Standard Error: %s' % stderr_val
    elif cmds[0].find('DTSTEnc_DUT') != -1:
        dir2mk = dstdir + cmds[len(cmds)-1][2:]
        cmdline = cygwin_dir +'mkdir --parents ' + dir2mk
        stdout_val, stderr_val = external_cmd(cmdline)
        cmds[len(cmds)-1] = cmds[len(cmds)-1][:2] + dstdir + cmds[len(cmds)-1][2:]
        for i in range(1, len(cmds)-1):
            if cmds[i].find('.\\Transcoder\\') != -1:
                cmds[i] = srcdir + cmds[i]
        line =  " ".join(cmds)
        stdout_val, stderr_val = external_cmd(line)


##### verify #####
#     print dir2mk
#     cmdline = cygwin_dir +'find ' + dir2mk + ' | grep wav | wc '
#     stdout_val, stderr_val = external_cmd(cmdline)
#     print 'Standard Output: %s' % stdout_val

#    Creating md5sum 
#     cmdline = cygwin_dir +'find ' + dir2mk 
#     stdout_val, stderr_val = external_cmd(cmdline)
#     print 'Standard Output: %s' % stdout_val
    cmdline = cygwin_dir +'find ' + dir2mk +  '| grep wav'
    stdout_val, stderr_val = external_cmd(cmdline)
#     print 'Standard Output: %s' % stdout_val
    filelist = stdout_val
    list = filelist.split()
    for line in list:
        cmdline = cygwin_dir +'md5sum ' + line
        stdout_val, stderr_val = external_cmd(cmdline)
        print '%s' % stdout_val    
        
    if bRemvoeFileAfterCheck:
        cmdline = cygwin_dir +'rm -rf ' + dir2mk
        stdout_val, stderr_val = external_cmd(cmdline)


#########################################################################
# http://ichart.finance.yahoo.com/table.csv?s=600036.ss
# we'd better use GoAgent to download all with no failure.
#########################################################################
class DoOneJob(workerpool.Job):
    "Job for downloading a given URL."
    def __init__(self, cmdline, taskid):
        self.cmdline = cmdline
        self.taskid = taskid
    def run(self):
        try:  
#             print 'task ', self.taskid, 'start'
            run_cmdline(self.cmdline)
#             print 'task ', self.taskid, 'stop'
            time.sleep(0.1)
        except:
            print 'DoOneJob failed.'

def do_multithread(cmdlines):
    global thread_num
    # Initialize a pool, 5 threads in this case
    pool = workerpool.WorkerPool(size=thread_num, maxjobs=20)
    cnt = 0
    for line in cmdlines:
        try:
            time.sleep(0.1)
            cnt += 1
            try:
                job = DoOneJob(line, cnt)
                pool.put(job)    
#                 print '-------------- put pool', cnt, pool.size(), pool.unfinished_tasks
                time.sleep(0.1)        
            except:
                print 'get  error'
                break
        except:
            break
        
    # Send shutdown jobs to all threads, and wait until all the jobs have been completed
    pool.shutdown()
    pool.wait()

def do_onethread(cmdlines):
#     print cmdlines
    cnt = 0
    for line in cmdlines:
        cnt += 1
        run_cmdline(line)
    print 'total', cnt
        

###########################################################################33    
if __name__ == '__main__':
    print 'start!'
    ISOTIMEFORMAT='%Y-%m-%d %X' 
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    f = open('cmdlog.txt')
    cmdlines = f.readlines()
#     do_onethread(cmdlines)
    do_multithread(cmdlines)
    f.close()
    print 'done'
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    exit()
