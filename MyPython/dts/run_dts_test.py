import time
import sys
import os
import string
import subprocess
import thread 
import workerpool

#
srcdir='D:'
#This is output dir, or ramdisk drive
cygwin_dir='c:\\cygwin\\bin\\'
nBackupFileNumEveryTime=10
bUseMultiCore = True
thread_num=8
bSaveCmdOutput = True

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

def external_cmd(cmd, msg_in=''):
#    print cmd
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
#    print line
    line = line.strip()
    line = line.replace('filename=', 'filename='+srcdir)
    line = line.replace('outputdir=D:\\DTS\\M8\\dts_test\\M8\\', 'outputdir='+dstdir )    
    
    cmds = line.split()
#     print len(cmds)
    if len(cmds) < 3:
        print 'parameter count < 3, error!', cmds
        return

##### Do decode #####    
#     if cmds[0].find('dts_decoder_dut') != -1:
#         return
    
#     for i in range(0, len(cmds)):
#         print i, cmds[i]
#     print '--'

    if cmds[0].find('dts_decoder_dut') != -1 or cmds[0].find('simg3') != -1:
        dir2mk = ''
        for i in range(1, len(cmds)):
            if cmds[i].find('outputdir') != -1:
                idx = cmds[i].find(dstdir)
                dir2mk= cmds[i][idx:]
                
#         print dir2mk
        cmdline = cygwin_dir +'mkdir --parents ' + dir2mk
#        print cmdline
        stdout_val, stderr_val = external_cmd(cmdline)
#        print 'Standard Output: %s' % stdout_val
#        print 'Standard Error: %s' % stderr_val
        
        line =  " ".join(cmds)
#        print line        
        stdout_val, stderr_val = external_cmd(line)
#        print 'Standard Output: %s' % stdout_val
#        print 'Standard Error: %s' % stderr_val
    elif cmds[0].find('DTSTEnc_DUT') != -1:
        dir2mk = dstdir + 'DTSTEnc_DUT\\'+ cmds[len(cmds)-1][2:]
        cmdline = cygwin_dir +'mkdir --parents ' + dir2mk
        stdout_val, stderr_val = external_cmd(cmdline)
        cmds[len(cmds)-1] = cmds[len(cmds)-1][:2] + dir2mk +'\\' + cmds[len(cmds)-1][2:]
        for i in range(1, len(cmds)-1):
            if cmds[i].find('.\\Transcoder\\') != -1:
                cmds[i] = srcdir + '\\DTS\\M8\\dts_test\\M8\\Transcoder\\DUTCreation_Material\\PCM\\' + cmds[i]
        line =  " ".join(cmds)
#        print line
        stdout_val, stderr_val = external_cmd(line)
    elif cmds[0].find('Neo6_dut') != -1:
        path_wavefile = cmds[1].split("\\\\")
        dirname = path_wavefile[len(path_wavefile)-1]
        idx = dirname.find('.wav')
        dirname = dirname[:idx]
        dir2mk = dstdir + 'Neo6_dut\\'+ dirname
        cmdline = cygwin_dir +'mkdir --parents ' + dir2mk
        #print cmdline
        stdout_val, stderr_val = external_cmd(cmdline)
        line =  " ".join(cmds)
        line += ' -outputdir='+dir2mk
        #print line
        stdout_val, stderr_val = external_cmd(line)

        
    if bSaveCmdOutput == True:
        fstdout.write(stdout_val+'\n')
        fstderr.write(stderr_val.strip()+'\n')

##### verify #####
    cmdline = cygwin_dir +'find ' + dir2mk +  '| grep wav'
    stdout_val, stderr_val = external_cmd(cmdline)
#    print 'Standard Output: %s' % stdout_val
    filelist = stdout_val
    list = filelist.split()
    for line in list:
        if len(line) < 5:
            continue
        cmdline = cygwin_dir +'md5sum ' + line
        stdout_val, stderr_val = external_cmd(cmdline)
        line = stdout_val.strip()
        print '%s' % line
        fw.write(line+'\n')
        fw.flush()    
        
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
            time.sleep(0.5)
        except:
            print 'DoOneJob failed.'

def do_multithread(cmdlines):
    global thread_num
    # Initialize a pool, 5 threads in this case
    pool = workerpool.WorkerPool(size=thread_num, maxjobs=16)
    cnt = 0
    runcnt = 0
    for line in cmdlines:
        try:
            time.sleep(0.1)
            cnt += 1
            try:
                job = DoOneJob(line, cnt)
                pool.put(job)    
                runcnt += 1
                print runcnt
                if runcnt > nBackupFileNumEveryTime and bBackupFileAfterCheck == True:
                    print 'Wait for Backup start ................ '
                    pool.wait()
                    while(pool.unfinished_tasks>0):
                        time.sleep(5)
                        print 'wait.'
                    print 'Doing Backup ........ '
                    do_backup()
                    time.sleep(0.2)
                    runcnt = 0
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
    runcnt = 0
    for line in cmdlines:
        cnt += 1
#        if cnt < 2220:
#            continue
        run_cmdline(line)
        runcnt += 1
        print runcnt
        if runcnt > nBackupFileNumEveryTime and bBackupFileAfterCheck == True:
            print 'Backuping ................ '
            time.sleep(2)
            do_backup()
            time.sleep(2)
            runcnt = 0
    print 'total', cnt
        
def do_backup():
    cmdline = cygwin_dir +'mkdir --parents ' + backdir
    stdout_val, stderr_val = external_cmd(cmdline)    

    for filename in os.listdir(dstdir):
        line = dstdir + filename
#         print line
        if os.path.isdir(line):
            cmdline = cygwin_dir +'cp -rf  ' + line + ' '+backdir
#             print cmdline
            stdout_val, stderr_val = external_cmd(cmdline)
#             print stdout_val, stderr_val 
            cmdline = cygwin_dir +'rm -rf  ' + line 
#            print cmdline
            stdout_val, stderr_val = external_cmd(cmdline)
#             print stdout_val, stderr_val 


###########################################################################33    
if __name__ == '__main__':
    print 'start! read cmds from cmdlog.txt....\n'
    ISOTIMEFORMAT='%Y-%m-%d %X' 
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    print 'Config:\n'
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
    
    if len(sys.argv) > 1:
        exit(0)
    
    print '\n\nWait 4s to start ... Ctrl+C to cancle now !\n'
    time.sleep(4)
    
#     do_backup()
#     exit()
  
    f = open('cmdlog.txt')
    fw = open('md5sum_log.txt', 'w')
    fstdout = open('stdout.txt', 'w')
    fstderr = open('stderr.txt', 'w')
    cmdlines = f.readlines()
    if bUseMultiCore == False:
        do_onethread(cmdlines)
    else:
        do_multithread(cmdlines)
    f.close()
    fw.close()
    fstdout.close()
    fstderr.close()
    print 'done'
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    exit()
