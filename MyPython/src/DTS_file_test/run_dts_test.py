# import time
# import sys
# import os
import string
import subprocess

srcdir='E:'
dstdir='I:\\temp\\'
cygwin_dir='d:\\cygwin\\bin\\'

def external_cmd(cmd, msg_in=''):
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

def convert_cmdline(line):
    print line
    line = line.replace('filename=', 'filename='+srcdir)
    line = line.replace('outputdir=D:\\DTS\\', 'outputdir='+dstdir )    
    
    cmds = line.split(' ')
#     for i in range(0, len(cmds)):
#         print i, cmds[i]

    if cmds[0].find('dts_decoder_dut') != -1:
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
        print line        
        stdout_val, stderr_val = external_cmd(line)
#         print 'Standard Output: %s' % stdout_val
#         print 'Standard Error: %s' % stderr_val
    
if __name__ == '__main__':
    f = open('cmdlog.txt')
    cnt = 0
    for line in f.readlines():
        print cnt, line
        print '---------------------------------------------------------------------------------------------------------------'
        convert_cmdline(line)
        cnt +=1
#         if cnt > 20:
#             break
        
    print 'total', cnt
    f.close()
    print 'done'
    pass