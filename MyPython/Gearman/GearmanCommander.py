#
# Scripts\easy_install.exe gearman
#
import time
import sys
import os
import string
import subprocess
import gearman

#
srcdir='D:'
#This is output dir, or ramdisk drive
cygwin_dir='c:\\cygwin\\bin\\'
nBackupFileNumEveryTime=10
bUseMultiCore = False
thread_num=8
bSaveCmdOutput = True
GearmanSrvIP = '10.10.32.93:4730'


#FAST TEST, NO BACKUP, FLY ON RAMDISK
dstdir='M:\\'
backdir='D:\\dts_dec_onfly_no_need_define\\'     # NOT USE. DEFINE ANYTHING YOU WANT.
bRemvoeFileAfterCheck = True         
bBackupFileAfterCheck = False           

#FAST TEST, BACKUP OUTPUT FILES
#dstdir='M:\\'                           # TEMP dir, set to RamDisk drive. 
#backdir='D:\\dts_dec_bak\\testing\\'
#bRemvoeFileAfterCheck = False          # bRemvoeFileAfterCheck be True for Ram Disk, because short of space.
#bBackupFileAfterCheck = True           # 'MOVE' output files to 'backdir' if True. 

#FAST TEST, OUTPUT TO DIRECTORY DIRECTLY
#dstdir='D:\\dts_dec_bak\\zsp_dev019_direct_20f\\'
#backdir='D:\\dts_dec_bak\\testing\\'
#bRemvoeFileAfterCheck = False
#bBackupFileAfterCheck = False           

RunningJobs = 0
Jobs = []

def check_request_status(job_request):
    if job_request.complete:
        print "Job %s finished!  Result: %s - \n%s" % (job_request.job.unique, job_request.state, job_request.result)
    elif job_request.timed_out:
        print "Job %s timed out!" % job_request.unique
    elif job_request.state == JOB_UNKNOWN:
        print "Job %s connection failed!" % job_request.unique

def gearman_run_cmdline(client, function, line):
    #print 'gearman_run_cmdline', line
    job_request = client.submit_job(function, line, background=False, wait_until_complete=False)
    Jobs.append(job_request)

def do_onethread(cmdlines):
    print cmdlines
    gm_client = gearman.GearmanClient([GearmanSrvIP])
    for i in range (0, 4):
        if cmdlines != '':
            gearman_run_cmdline(gm_client, 'runcmd', cmdlines)
        else:
            gearman_run_cmdline(gm_client, 'getsysinfo', cmdlines)
    gm_client.wait_until_jobs_completed(Jobs)
    for job in Jobs:
        check_request_status(job)
        
###########################################################################33    
if __name__ == '__main__':
    print 50*'*'
    print 15*'*', 'GearmanCommander start!'
    print 50*'*'
    
    print len(sys.argv)
    if len(sys.argv) > 1:
        do_onethread(sys.argv[1])
    else:
        do_onethread('')

    print 'done'
    exit()
