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
import subprocess
import workerpool

POLL_TIMEOUT_SECONDS = 30
SCRIPT_VERSION = 'V1.0.4'

#
srcdir='D:'
#This is output dir, or ramdisk drive
cygwin_dir='c:\\cygwin\\bin\\'
nBackupFileNumEveryTime=10
bUseMultiCore = True
thread_num=8
bSaveCmdOutput = True
GearmanSrvIP = '10.10.32.93:4730'
runcnt = 0
currdir = ''

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
        self._exit_runloop = False
        return super(CustomGearmanWorker, self).__init__(host_list)
    def on_job_execute(self, current_job):
        global jobnum
        # print "Job started" , jobnum
        jobnum += 1
        return super(CustomGearmanWorker, self).on_job_execute(current_job)
    def after_poll(self, any_activity):
        return self.exit_poll
    def exit_request(self, b_exit):
        self.exit_poll = b_exit
    def stopwork(self):
        self._exit_runloop = True
        print 'stopwork() called...'
    # OVERRIDDEN
    def work(self, poll_timeout=POLL_TIMEOUT_SECONDS):
        worker_connections = []
        continue_working = True

        def continue_while_connections_alive(any_activity):
            return self.after_poll(any_activity)

        while continue_working and not self._exit_runloop:
            worker_connections = self.establish_worker_connections()
            continue_working = self.poll_connections_until_stopped(
                worker_connections,
                continue_while_connections_alive,
                timeout=poll_timeout)

        for current_connection in worker_connections:
            current_connection.close()

        self.shutdown()
        print 'CustomGearmanWorker shutdown...'
        
def external_cmd(cmd, rundir, msg_in=''):
    # print rundir, cmd
#     return None, None
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   cwd=rundir
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        # time.sleep(0.2)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None

def run_cmdline(cnt, line):
    # print line
    # global currdir
    one = line
    temp = one.split(' ')
    profile_fname = temp[len(temp)-1]
    # dir2mk = "tmp_%04d"%cnt
    dir2mk = 'tmpdir_' + profile_fname.replace('.log','')
    temp[len(temp)-2] = temp[len(temp)-2].replace('~/tmp/0.hevc', './'+dir2mk+'.hevc' )
    onecmd = ' '.join(temp[:len(temp)-1])
    # print dir2mk, profile_fname, onecmd
    cmdline = 'mkdir ' + dir2mk
    stdout_val, stderr_val = external_cmd(cmdline, './')
    # print stdout_val, stderr_val
    cmdline = onecmd
    # print onecmd
    stdout_val, stderr_val = external_cmd(cmdline, './'+dir2mk)    
    # print stdout_val, stderr_val
    cmdline = 'mv ' + 'profile.log ' + '../'+profile_fname
    stdout_val, stderr_val = external_cmd(cmdline, './'+dir2mk)    
    # print stdout_val, stderr_val
    cmdline = 'rm -rf ' + dir2mk
    stdout_val, stderr_val = external_cmd(cmdline, './')
    fp = open(profile_fname, 'rb')
    data = fp.read()
    fp.close
    return data


def run_hevc(gearman_worker, gearman_job):
    global runcnt
    line = gearman_job.data
    runcnt += 1
    print '[  ' + str(runcnt) + '  ]'
    print line
    return run_cmdline(runcnt, line)


class CreatThread_DTS_Test (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('hevc-worker')
        self.worker.register_task('hevc', run_hevc)  
        self.worker.register_task('hevc_' + socket.gethostname() , run_hevc)
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
    # global cpu_infos
    # ret_line += 'CPU INFO: ' + cpu_infos + '\n'
    # ret_line += 'CPU NUM: '+ str(psutil.cpu_count()) + '\n'
    # ret_line += 'CPU PERCENT: '+ str(psutil.cpu_percent(interval=1, percpu=True)) + '\n'
    # print ret_line
    # disks_after = psutil.disk_io_counters()
    # disks_read_per_sec = disks_after.read_bytes - disks_before.read_bytes
    # disks_write_per_sec = disks_after.write_bytes - disks_before.write_bytes
    # ret_line += 'DISK READ/WIRTE: ' + bytes2human(disks_read_per_sec) + '/s, ' + bytes2human(disks_write_per_sec) +'/s' + '\n'
    # ret_line += 'DISK M USAGE: '+ 'total:'+bytes2human(psutil.disk_usage('M:').total) + ', free:'+bytes2human(psutil.disk_usage('M:').free) +  '\n'
    # ret_line += 35*'*' + '\n'
    print str(ret_line)
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
        self.worker.set_client_id('hevc-getinfo')
        # self.worker.register_task('getsysinfo', get_sysinfo)        
        self.worker.register_task('HOST_' + socket.gethostname() + '_' + SCRIPT_VERSION, run_hevc)

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
        self.worker.set_client_id('hevc-runcmd')
        # self.worker.register_task('runcmd', run_ext_command)        
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
    print 'Exiting workers ... wait 30s'
    global workers
    #print 'workers num', len(workers)
    i = 0
    for worker in workers:
        print 'worker stopping', i
        print '.',
        i+=1
        worker.exit_request(False)
        worker.stopwork()
    workers = []

    global threads
    #print 'theads num', len(threads)
    i = 0
    for thread in threads:
        print 'thread stopping', i
        i+=1
        thread.join()
    threads = []
    time.sleep(1)
    return 'HOST: '+ socket.gethostname() + '\n'+'run_exit_workers done\n'

def run_exit_workers(gearman_worker, gearman_job):
    return exit_workers()

class CreatThread_ExitWorkers (threading.Thread): 
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.worker = CustomGearmanWorker([GearmanSrvIP])
        self.worker.set_client_id('hevc-runcmd')
        self.worker.register_task('exit_workers', run_exit_workers)        
        self.id = id
        global workers
        workers.append(self.worker)
    def run(self):                   
        print 'Job exit_workers', self.id, 'ready!'
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
     

############    debug ##########

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
        
class DoOneJob(workerpool.Job):
    "Job for downloading a given URL."
    def __init__(self, cmdline, taskid):
        self.cmdline = cmdline
        self.taskid = taskid
    def run(self):
        try:  
            # print 'task ', self.taskid, 'start'
            run_cmdline(self.taskid, self.cmdline)
            # print 'task ', self.taskid, 'stop'
            # time.sleep(0.5)
        except:
            print 'DoOneJob failed.'       

def Do_OneThread(cmds):    
    index = 0    
    for one in cmds:
        index += 1
        run_cmdline(index, one)
        print one
        break
            
            
def Do_MultiThread(cmds):
    global thread_num
    pool = workerpool.WorkerPool(size=thread_num, maxjobs=4)
    cnt = 0
    runcnt = 0
    for line in cmds:
        try:
            cnt += 1
            print 'Job', cnt, 
            try:
                job = DoOneJob(line, cnt)
                pool.put(job)    
                runcnt += 1
                # print runcnt
                # time.sleep(0.1)
                # break
            except:
                print 'get  error'
                break
        except:
            break
        
    # Send shutdown jobs to all threads, and wait until all the jobs have been completed
    pool.shutdown()
    pool.wait()        
        
def debug_multithread():
    print 'start! ...\n'
    start = time.time()

    cmds = get_cmds()
    # if False:
        # Do_OneThread(cmds)
    # else:
    Do_MultiThread(cmds)

    print 'Done.'
    end = time.time()
    elapsed = float('%.2f' %(end - start))
    print "Time taken: ", elapsed, "seconds."        
        
    
###########################################################################33    
if __name__ == '__main__':
    # global threads
    if False:
        debug_multithread()
        exit(0)
    
    print 50*'*'
    print 15*'*', 'Gearman Worker start!'
    print 50*'*'
    ISOTIMEFORMAT='%Y-%m-%d %X' 
    print time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    print 'Config:'
    # print '\tsrcdir = ', srcdir
    # print '\tdstdir = ', dstdir
    # print '\tbackdir = ', backdir
    # print '\tcygwin_dir = ', cygwin_dir
    # print '\tbRemvoeFileAfterCheck = ', bRemvoeFileAfterCheck
    # print '\tbBackupFileAfterCheck = ', bBackupFileAfterCheck
    print '\tbUseMultiCore = ', bUseMultiCore
    # print '\tnBackupFileNumEveryTime = ', nBackupFileNumEveryTime
    print '\tthread_num = ', thread_num
    # print '\tbSaveCmdOutput = ', bSaveCmdOutput
    print '\tGearmanSrvIP = ', GearmanSrvIP

    fstdout = open('stdout.txt', 'w') 
    fstderr = open('stderr.txt', 'w')	
	
    for thead_index in range(0,thread_num):
        thread1 = CreatThread_DTS_Test(thead_index)
        thread1.start()
        threads.append(thread1)
        time.sleep(0.2)
    
    # thread1 = CreatThread_GetInfo(0)
    # thread1.start()
    #threads.append(thread1)
    time.sleep(0.2)
    
    # thread1 = CreatThread_RunCmd(0)
    # thread1.start()
    #threads.append(thread1)
    time.sleep(0.2)
    
    # getcpuInfo()
    # print get_sysinfo_string()
    print '\nRegister_task done! Waiting for commands... Ctrl+C to exit.\n'

    check_exit_workers()
	
    fstdout.close()
    fstderr.close()	
	
    print 'All Exit! All Done!'
    time.sleep(1)

