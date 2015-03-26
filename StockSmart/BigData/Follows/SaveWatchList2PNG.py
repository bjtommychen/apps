import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import subprocess

save_path = './save_png/'
csv_path = ''  #e:\\KuaiDisk\\StockSmart\\follows\\
        
def external_cmd(cmd, rundir='./', msg_in=''):
    # print 'rundir:',rundir, ', cmds:', cmd
    # return 'stdout', 'stderr'
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

if  __name__ == '__main__':
    print '#'*60
    print '##### Convert Watch List to PNG files.'
    print '#'*60

    if True:
        filename  = csv_path+"watch_cn.csv"
        reader = csv.reader(file(filename,'rb'))
        i = 0
        for one in reader:
            code = one[1]
            cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ "cn_W%02d_"%i+code+'.png'
            print cmdline
            external_cmd(cmdline)
            i+= 1
            
        filename  = csv_path+"hold_cn.csv"
        reader = csv.reader(file(filename,'rb'))
        i = 0
        for one in reader:
            code = one[1]
            cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ "cn_H%02d_"%i+code+'.png'
            print cmdline
            external_cmd(cmdline)
            i+= 1

    if True:
        filename  = csv_path+"watch_hk.csv"
        reader = csv.reader(file(filename,'rb'))
        i = 0
        for one in reader:
            code = one[1]
            cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ "hk_W%02d_"%i+code+'.png'
            print cmdline
            external_cmd(cmdline)
            i+= 1
            
        filename  = csv_path+"hold_hk.csv"
        reader = csv.reader(file(filename,'rb'))
        i = 0
        for one in reader:
            code = one[1]
            cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ "hk_H%02d_"%i+code+'.png'
            print cmdline
            external_cmd(cmdline)
            i+= 1    
            
    if True:
        filename  = csv_path+"watch_us.csv"
        reader = csv.reader(file(filename,'rb'))
        i = 0
        for one in reader:
            code = one[1]
            cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ "us_W%02d_"%i+code+'.png'
            print cmdline
            external_cmd(cmdline)
            i+= 1
            
        filename  = csv_path+"hold_us.csv"
        reader = csv.reader(file(filename,'rb'))
        i = 0
        for one in reader:
            code = one[1]
            cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ "us_H%02d_"%i+code+'.png'
            print cmdline
            external_cmd(cmdline)
            i+= 1                 