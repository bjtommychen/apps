# -*- coding: utf-8 -*
import time, datetime
import sys
import os, psutil
import socket
import platform

start = time.time()
cpu_infos = ''   

   
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
    getcpuInfo()
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
    #ret_line += 'DISK M USAGE: '+ 'total:'+bytes2human(psutil.disk_usage('M:').total) + ', free:'+bytes2human(psutil.disk_usage('M:').free) +  '\n'
    ret_line += 35*'*' + '\n'
    #print str(ret_line)
    return ret_line    
    
    
def sys_process_cmds(cmds):
    print 'sys_process_cmds', cmds
    string = ''
    if (len(cmds) == 0):
        string += 'sys help - for more.'
    else:    
        if cmds[0] == 'help' or cmds[0] == '?':
            string += 'sys help:\n'+ \
                '\thelp - print help \n' +\
                '\tinfo - print system info \n' +\
                '\tuptime - print uptime \n' +\
                ''
        if cmds[0] == 'info':
            string += get_sysinfo_string()             
        if cmds[0] == 'uptime':
            text = str(datetime.timedelta(seconds=int((time.time() - start))))
            string += text             
                
    return string    