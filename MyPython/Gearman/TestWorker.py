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
import platform


POLL_TIMEOUT_SECONDS = 30
SCRIPT_VERSION = 'V1.0.1'

#
srcdir='D:'
#This is output dir, or ramdisk drive
cygwin_dir='c:\\cygwin\\bin\\'
nBackupFileNumEveryTime=10
bUseMultiCore = True
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

threads = []
workers = []
jobnum = 0
cpu_infos = ''   

class CustomGearmanWorker(gearman.GearmanWorker):
    def __init__(self, host_list=None):
        self.exit_poll = True
        return super(CustomGearmanWorker, self).__init__(host_list)
    def on_job_execute(self, current_job):
        global jobnum
        print "Job started" , jobnum
        jobnum += 1
        return super(CustomGearmanWorker, self).on_job_execute(current_job)
    def after_poll(self, any_activity):
        return self.exit_poll
    def exit_request(self, b_exit):
        self.exit_poll = b_exit

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
        self.worker.register_task('dts_test_' + socket.gethostname() , run_dts_test)
        self.id = id
        global workers
        workers.append(self.worker)
    def run(self):                   
        print 'worker', self.id, 'ready!'
        try:
            self.worker.work(poll_timeout=POLL_TIMEOUT_SECONDS)
        except:
            print 'thread run error'
        #print 'worker', self.id, 'run done!'
    def stop(self):
        print 'worker', self.id, 'stop!'


#####################################################################################################333        
        
def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K/s'
    >>> bytes2human(100001221)
    '95.4 M/s'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        #print i, s
        prefix[s] = 1 << (i + 1) * 10
        #print prefix[s]
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)

def getSYSTEM():
    return platform.system()    

 
def getcpuInfo():
    """cpuwindows)/linux"""
    CPUINFO = "None"
    sys = getSYSTEM()
    if  sys == "Windows":
        import wmi
        try:
            c = wmi.WMI()
        except wmi.x_wmi, x: # Py3+ except wmi.x_wmi as x:
            print "Exception number", wmi.x_wmi, x           
        for cpu in c.Win32_Processor():
            lines = cpu.Name
            CPUINFO = lines.strip()
    elif sys == "Linux":
        try:        
            infos = "cat /proc/cpuinfo | grep 'model name' | awk -F: '{print $2}'"
            info = os.popen(infos).read()
            CPUINFO = info.strip()
        except:
            pass
    else:
        pass
    global cpu_infos
    cpu_infos = CPUINFO.encode('ascii')
    return
    
def get_sysinfo_string():
    disks_before = psutil.disk_io_counters()
    ret_line = ''
    ret_line += 10*'*' + ' ' + socket.gethostname()  + ' ' + 10*'*' + '\n'
    ret_line += 'HOST: '+ socket.gethostname() + '\n'
    #print ret_line
    global cpu_infos
    ret_line += 'CPU INFO: ' + cpu_infos + '\n'
    ret_line += 'CPU NUM: '+ str(psutil.cpu_count()) + '\n'
    ret_line += 'CPU PERCENT: '+ str(psutil.cpu_percent(interval=1, percpu=True)) + '\n'
    #print ret_line
    disks_after = psutil.disk_io_counters()
    disks_read_per_sec = disks_after.read_bytes - disks_before.read_bytes
    disks_write_per_sec = disks_after.write_bytes - disks_before.write_bytes
    ret_line += 'DISK READ/WIRTE: ' + bytes2human(disks_read_per_sec) + '/s, ' + bytes2human(disks_write_per_sec) +'/s' + '\n'
    ret_line += 'DISK M USAGE: '+ 'total:'+bytes2human(psutil.disk_usage('M:').total) + ', free:'+bytes2human(psutil.disk_usage('M:').free) +  '\n'
    ret_line += 35*'*' + '\n'
    #print str(ret_line)
    return ret_line
    
def get_sysinfo(gearman_worker, gearman_job):
    print gearman_job.data
    ret_line = (get_sysinfo_string())
    print 'get_sysinfo:', ret_line
    return ret_line
        
class CreatThread_GetInfo (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('dts-test-getinfo')
        self.worker.register_task('getsysinfo', get_sysinfo)        
        self.worker.register_task('HOST_' + socket.gethostname() + '_' + SCRIPT_VERSION, run_dts_test)

        self.id = id
        global workers
        workers.append(self.worker)
    def run(self):                   
        print 'getsysinfo', self.id, 'ready!'
        try:
            self.worker.work(poll_timeout=POLL_TIMEOUT_SECONDS)        
        except:
            print 'thread run error'
    def stop(self):
        print 'worker', self.id, 'stop!'
        
#####################################################################################33        
def run_ext_command(gearman_worker, gearman_job):
    cmdline = gearman_job.data
    print 'run_ext_command:', cmdline
    stdout_val, stderr_val = external_cmd(cmdline)
    time.sleep(5)
    return '['+socket.gethostname()+']\n'+stdout_val
  
class CreatThread_RunCmd (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('dts-test-runcmd')
        self.worker.register_task('runcmd', run_ext_command)        
        self.id = id
        global workers
        workers.append(self.worker)
    def run(self):                   
        print 'runcmd', self.id, 'ready!'
        try:
            self.worker.work(poll_timeout=POLL_TIMEOUT_SECONDS)     
        except:
            print 'thread run error'        
    def stop(self):
        print 'worker', self.id, 'stop!'
        
###################################################################3    
def exit_workers():
    print 'Exiting workers ...'
    global workers
    #print 'workers num', len(workers)
    i = 0
    for worker in workers:
        #print 'worker stopping', i
        print '.',
        i+=1
        worker.exit_request(False)
    workers = []

    global threads
    #print 'theads num', len(threads)
    i = 0
    for thread in threads:
        #print 'thread stopping', i
        i+=1
        thread.join()
    threads = []
    time.sleep(5)
    return 'HOST: '+ socket.gethostname() + '\n'+'run_exit_workers done\n'

def run_exit_workers(gearman_worker, gearman_job):
    return exit_workers()

class CreatThread_ExitWorkers (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('dts-test-runcmd')
        self.worker.register_task('exit_workers', run_exit_workers)        
        self.id = id
        global workers
        workers.append(self.worker)
    def run(self):                   
        print 'exit_workers', self.id, 'ready!'
        try:
            self.worker.work(poll_timeout=POLL_TIMEOUT_SECONDS)      
        except:
            print 'thread run error'
    def stop(self):
        print 'worker', self.id, 'stop!'
    
def check_exit_workers():
    thread1 = CreatThread_ExitWorkers(0)
    thread1.start()
    
    try:
        global threads
        
        while len(threads)>0:
            #print 'checking @'
            #print len(threads)
            threads_alive = False
            for thread in threads:
                threads_alive |= thread.isAlive()
                #print thread.isAlive()
            if not threads_alive:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print 'Exception!'
    finally:
        exit_workers()
        
    
###########################################################################33    
if __name__ == '__main__':
    #global threads

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

    fstdout = open('stdout.txt', 'w')
    fstderr = open('stderr.txt', 'w')	
	
    for index in range(0,thread_num):
        thread1 = CreatThread_DTS_Test(index)
        thread1.start()
        threads.append(thread1)
        time.sleep(0.2)
    
    thread1 = CreatThread_GetInfo(0)
    thread1.start()
    #threads.append(thread1)
    time.sleep(0.2)
    
    thread1 = CreatThread_RunCmd(0)
    thread1.start()
    #threads.append(thread1)
    time.sleep(0.2)
    
    getcpuInfo()
    print get_sysinfo_string()
    print '\nRegister_task done! Waiting for commands... Ctrl+C to exit.\n'

    check_exit_workers()
	
    fstdout.close()
    fstderr.close()	
	
    print 'All Exit! All Done!'
    time.sleep(5)

