#
# Scripts\easy_install.exe gearman
#
import time
import sys
import os, psutil
import string
import subprocess
import gearman
import threading
import socket

#
srcdir='D:'
#This is output dir, or ramdisk drive
cygwin_dir='c:\\cygwin\\bin\\'
nBackupFileNumEveryTime=10
bUseMultiCore = True
thread_num=8
bSaveCmdOutput = False
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

jobnum = 0
class CustomGearmanWorker(gearman.GearmanWorker):
    def on_job_execute(self, current_job):
        global jobnum
        print "Job started" , jobnum
        jobnum += 1
        return super(CustomGearmanWorker, self).on_job_execute(current_job)


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

def run_dts_test(gearman_worker, gearman_job):
    line = gearman_job.data
    #print line
    line = line.strip()
    line = line.replace('filename=', 'filename='+srcdir)
    line = line.replace('outputdir=D:\\DTS\\M8\\dts_test\\M8\\', 'outputdir='+dstdir )    
    
    cmds = line.split()
#     print len(cmds)
    if len(cmds) < 3:
        print 'parameter count < 3, error!', cmds
        return ' '

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
                
        #print dir2mk
        cmdline = cygwin_dir +'mkdir --parents ' + dir2mk
        #print cmdline
        stdout_val, stderr_val = external_cmd(cmdline)
        #print 'Standard Output: %s' % stdout_val
        #print 'Standard Error: %s' % stderr_val
        
        line =  " ".join(cmds)
        #print line        
        stdout_val, stderr_val = external_cmd(line)
        #print 'Standard Output: %s' % stdout_val
        #print 'Standard Error: %s' % stderr_val
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
    #print 'Standard Output: %s' % stdout_val
    filelist = stdout_val
    list = filelist.split()
    return_line = ''
    for line in list:
        if len(line) < 5:
            continue
        cmdline = cygwin_dir +'md5sum ' + line
        #print cmdline
        stdout_val, stderr_val = external_cmd(cmdline)
        line = stdout_val.strip()
        print '%s' % line
        return_line +=line + '\n'
        #fw.write(line+'\n')
        #fw.flush()    
        
    if bRemvoeFileAfterCheck:
        cmdline = cygwin_dir +'rm -rf ' + dir2mk
        #print cmdline
        stdout_val, stderr_val = external_cmd(cmdline)
    
    #print 'return: ', return_line
    return return_line

class CreatThread_DTS_Test (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('dts-test-worker')
        self.worker.register_task('dts_test', run_dts_test)        
        self.id = id
    def run(self):                   
        print 'worker', self.id, 'ready!'
        self.worker.work()

def get_sysinfo(gearman_worker, gearman_job):
    print gearman_job.data
    ret_line = ''
    ret_line += 10*'*' + ' ' + socket.gethostname()  + ' ' + 10*'*' + '\n'
    ret_line += 'HOST: '+ socket.gethostname() + '\n'
    ret_line += 'CPU NUM: '+ str(psutil.cpu_count()) + '\n'
    ret_line += 'CPU PERCENT: '+ str(psutil.cpu_percent(interval=5, percpu=True)) + '\n'
    ret_line += 'DISK M USAGE: '+ str(psutil.disk_usage('M:')) + '\n'
    ret_line += 35*'*' + '\n'
    print 'get_sysinfo:', ret_line
    return ret_line
   
        
class CreatThread_GetInfo (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('dts-test-getinfo')
        self.worker.register_task('getsysinfo', get_sysinfo)        
        self.id = id
    def run(self):                   
        print 'getsysinfo', self.id, 'ready!'
        self.worker.work()        

def run_ext_command(gearman_worker, gearman_job):
    cmdline = gearman_job.data
    print 'run_ext_command:', cmdline
    stdout_val, stderr_val = external_cmd(cmdline)
    return stdout_val
  
class CreatThread_RunCmd (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('dts-test-runcmd')
        self.worker.register_task('runcmd', run_ext_command)        
        self.id = id
    def run(self):                   
        print 'runcmd', self.id, 'ready!'
        self.worker.work()      
    
###########################################################################33    
if __name__ == '__main__':
    print 50*'*'
    print 15*'*', 'Gearman Worker start!'
    print 50*'*'
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

    for index in range(0,thread_num):
        thread1 = CreatThread_DTS_Test(index)
        thread1.start()
        time.sleep(0.2)
    thread1 = CreatThread_GetInfo(0)
    thread1.start()
    time.sleep(0.2)
    thread1 = CreatThread_RunCmd(0)
    thread1.start()
    time.sleep(0.2)
    print '\nRegister_task done! Waiting for commands...\n'

