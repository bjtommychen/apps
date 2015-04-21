import os
import stat,fnmatch
import csv
import time
import sys
import os
import subprocess

def external_cmd(cmd, rundir='./', msg_in=''):
    print 'rundir:',rundir, ', cmds:', cmd
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

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            # print fullname
            st = os.lstat(fullname)
            if stat.S_ISDIR(st.st_mode) and subdir:
                dirlist += getFileList(fullname,ext)
            elif os.path.isfile(fullname):
                if fnmatch.fnmatch( fullname, ext): 
                    dirlist.append(fullname)
                else:
                    pass
        return dirlist
    else:
        return [] 
        
# sh20150306.rar        
def getQDAfile(filename='sh20150306.rar'):
    print (' Processing '+filename+' ').center(79, '-')
    outputfilename = 'input_qda/Quote' + filename[2:].replace('.rar', '') + '.QDA'
    if os.path.exists(outputfilename):
        print outputfilename, 'exist, Skip !'
        return
    cmds = 'wget ftp://datadown:88158@down.58851.com/gpday/' + filename
    stdout_msg, stderr_msg = external_cmd(cmds)
    print stdout_msg + stderr_msg
    if not os.path.exists(filename):
        print filename, 'Not exist, Skip !'
        return
    
    cmds = 'rar e -o+ ' + filename
    stdout_msg, stderr_msg = external_cmd(cmds)
    print stdout_msg + stderr_msg

    cmds = 'mv -f Quote.QDA ' + outputfilename
    stdout_msg, stderr_msg = external_cmd(cmds)
    print stdout_msg + stderr_msg

    # cmds = 'mv -f ' + filename + ' input_qda1m/'
    cmds = 'rm -f ' + filename
    stdout_msg, stderr_msg = external_cmd(cmds)
    print stdout_msg + stderr_msg
    
def get_DateString():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())    
      
def get_QDA_recentdays(days=7):
    for i in range(0, days):
        timestamp = time.localtime(time.time()-3600*24*i)
        timestr = time.strftime('%Y%m%d', timestamp)
        filename = 'sh'+timestr+'.rar'
        getQDAfile(filename)
        
        
########################################################################
if __name__ == '__main__':
    # getQDAfile()
    get_QDA_recentdays(3)
    
    