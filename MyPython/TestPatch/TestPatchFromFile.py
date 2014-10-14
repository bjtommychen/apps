import time
import sys
import os
import string
import subprocess
import thread 
import argparse
import threading
import workerpool

bSaveCmdOutput = True
bUseMultiCore = True
thread_num=8
curr_thread = 0     

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

def run_cmdline(line):
    global bSaveCmdOutput
    stdout_val, stderr_val = external_cmd(line)
    # print 'Standard Output: %s' % stdout_val
    # print 'Standard Error: %s' % stderr_val

    if bSaveCmdOutput == True:
        fstdout.write(stdout_val+'\n')
        fstderr.write(stderr_val.strip()+'\n')

   
def DoOneJob(cmdline):
    global curr_thread
    run_cmdline(cmdline)
    curr_thread -= 1
        
class DoOneJob(workerpool.Job):
    "Job for downloading a given URL."
    def __init__(self, cmdline, taskid):
        self.cmdline = cmdline
        self.taskid = taskid
    def run(self):
        try:  
            # print 'task ', self.taskid, 'start'
            run_cmdline(self.cmdline)
            # print 'task ', self.taskid, 'stop'
            time.sleep(0.5)
        except:
            print 'DoOneJob failed.'

def do_multithread(cmdlines):
    global thread_num
    # print thread_num
    # Initialize a pool, 5 threads in this case
    pool = workerpool.WorkerPool(size=thread_num, maxjobs=4)
    cnt = 0
    runcnt = 0
    for line in cmdlines:
        try:
            cnt += 1
            print 'Job', cnt
            try:
                job = DoOneJob(line, cnt)
                pool.put(job)    
                runcnt += 1
                # print runcnt
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
    # print cmdlines
    cnt = 0
    runcnt = 0
    for line in cmdlines:
        cnt += 1
        print 'Job', cnt
        if cnt > 2:
           break
        DoOneJob(line)
        runcnt += 1
    print 'Total', cnt
        

###########################################################################33    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename', default='cmdlog.txt', help='Specify the command line file. Default: cmdlog.txt')
    parser.add_argument('-j', action='store', dest='threads', default=1, help='Specify multi-hreads number. Default: 1') 
    parser.add_argument('--noout', action='store_true', default=False, dest='not_output', help='Disable stdout/stderr output to file.')
    parser.add_argument('--debug', action='store_const', dest='debug',default=0, const=1, help='Enable debug mode.') 
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()  	
    
    if len(sys.argv) < 1:
        exit(0)

    print 'start! ...\n'
    bUseMultiCore = False		
    if args.threads > 1:
        bUseMultiCore = True
    if args.not_output:
        bSaveCmdOutput = False
    thread_num = int(args.threads)        
    
    print 'Config:'
    print '\tbUseMultiCore = ', bUseMultiCore
    print '\tThread_num = ', thread_num		
    print '\tbSaveCmdOutput = ', bSaveCmdOutput

    start = time.time()
    
    f = open(args.filename)
    fstdout = open('stdout.txt', 'w')
    fstderr = open('stderr.txt', 'w')    
    cmdlines = f.readlines()
    if bUseMultiCore == False:
        do_onethread(cmdlines)
    else:
        do_multithread(cmdlines)
    f.close()
    fstdout.close()
    fstderr.close()
    
    print 'Done.'
    end = time.time()
    elapsed = float('%.2f' %(end - start))
    print "Time taken: ", elapsed, "seconds."
    exit()
