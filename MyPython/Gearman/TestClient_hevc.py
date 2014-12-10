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
Job_Name = "hevc"

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
        # print "Job %s finished!  Result: %s - \n%s" % (job_request.job.unique, job_request.state, job_request.result)
        if job_request.result != '':
            data = job_request.result
            cmdline = job_request.gearman_job.data
            temp = cmdline.split(' ')
            profile_fname = temp[len(temp)-1]
            fw = open(profile_fname, 'wb')
            fw.write(data)
            fw.close() 
            # print job_request.result,
            # fw.write(job_request.result)
            # fw.flush()    
    elif job_request.timed_out:
        print "Job %s timed out!" % job_request.unique
    elif job_request.state == JOB_UNKNOWN:
        print "Job %s connection failed!" % job_request.unique

def gearman_run_cmdline(client, line):
    #print 'gearman_run_cmdline', line
    job_request = client.submit_job(Job_Name, line, background=False, wait_until_complete=False)
    global RunningJobs
    global Jobs
    RunningJobs += 1
    #print 'job_request', job_request
    Jobs.append(job_request)
    #check_request_status(job_request)

def do_onethread(cmdlines):
#     print cmdlines
    gm_client = gearman.GearmanClient([GearmanSrvIP])
    cnt = 0
    runcnt = 0
    global Jobs
    for line in cmdlines:
        # while len(Jobs) > 8:
            # break
            # not use now
            # for job in Jobs:
                # if gm_client.get_job_status(job).state != 'COMPLETE':
                    # time.sleep(0.1)
                    # continue
                # print 'find one completed.'
                # check_request_status(job)
                # Jobs.remove(job)
                # break
            # time.sleep(0.1)
            
        #if cnt > 50:
        #    break
        # print '[  ' + str(runcnt) + '  ]'
        gearman_run_cmdline(gm_client, line)
        cnt += 1
        runcnt += 1
        #print 'Jobs', len(Jobs)
    print 'total', cnt
    print 'wait for all completed...'

    gm_client.wait_until_jobs_accepted(Jobs)
    #gm_client.wait_until_jobs_completed(Jobs, poll_timeout= 5.0)
    cnt_completed = 0;
    while(True):
        #statuses = gm_client.get_job_statuses(Jobs)
        #print statuses
        #print len(Jobs)
        gm_client.wait_until_jobs_completed(Jobs, poll_timeout= 1)
        cnt_completed = 0
        for job in Jobs:
            #wait_jobs = []
            #wait_jobs.append(job)
            #gm_client.wait_until_jobs_completed(wait_jobs)
            if job.complete:
                cnt_completed += 1
        print cnt_completed , '/', cnt, 'done!'
        if (cnt_completed >= cnt):
            break
        time.sleep(30)

    gm_client.wait_until_jobs_completed(Jobs)
    for job in Jobs:
        check_request_status(job)
    #    print gm_client.get_job_status(job)

    print 'done.'

def get_cmds():  
    fp = open('cmd.sh', 'rb')
    lines = fp.readlines()
    # print lines, len(lines)
    cmds = []
    onecmd = ''
    # make it simple
    for one in lines:
        # print one
        one = one.strip()
        # print len(one)
        if len(one) < 1:
            continue
        if one.find('hevc_testenc') != -1:
            onecmd += one.replace('\n',' ')
            continue
        if one.find('profile.log') != -1:
            temp = one.split(' ')
            # print len(temp)
            onecmd += ' ' + temp[2]
            # print onecmd
            cmds.append(onecmd)
            onecmd = ''
    cmds_out = []
    for one in cmds:
        temp = one.split(' ')
        temp[0] = temp[0].replace('../hevc_testenc', '../hevc_testenc')
        temp[len(temp)-1] = temp[len(temp)-1].replace('../','')
        cmds_out.append(' '.join(temp))
        # print ' '.join(temp)
    return cmds_out    
    
###########################################################################33    
if __name__ == '__main__':
    print 50*'*'
    print 15*'*', 'Client start!'
    print 50*'*'
    print 'Read cmds from cmdlog.txt....\n'
    ISOTIMEFORMAT='%Y-%m-%d %X' 
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    print 'Config:'
    print '\tsrcdir = ', srcdir
    print '\tdstdir = ', dstdir
    print '\tbackdir = ', backdir
    print '\tcygwin_dir = ', cygwin_dir
    print '\tbRemvoeFileAfterCheck = ', bRemvoeFileAfterCheck
    print '\tbBackupFileAfterCheck = ', bBackupFileAfterCheck
    print '\tbUseMultiCore = ', bUseMultiCore
    print '\tnBackupFileNumEveryTime = ', nBackupFileNumEveryTime
    print '\tthread_num = ', thread_num
    print '\tbSaveCmdOutput = ', bSaveCmdOutput
    print '\tGearmanSrvIP = ', GearmanSrvIP
    
    if len(sys.argv) > 1:
        exit(0)
    
    print '\n\nWait 4s to start ... Ctrl+C to cancle now !\n'
    #time.sleep(4)
    
#     do_backup()
#     exit()
  
    # f = open('cmd.sh')
    # fw = open('md5sum_log.txt', 'w')
    # fstdout = open('stdout.txt', 'w')
    # fstderr = open('stderr.txt', 'w')
    cmdlines = get_cmds()

    do_onethread(cmdlines)

    # f.close()
    # fw.close()
    # fstdout.close()
    # fstderr.close()
    print 'done'
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    exit()
