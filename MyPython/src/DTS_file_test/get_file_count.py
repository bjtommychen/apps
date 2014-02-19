import time
import sys
import os

import subprocess

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
        #log("ValueError: %s" % err)
        return None, None
    except IOError as err:
        #log("IOError: %s" % err)
        return None, None
                               
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
if  __name__ == '__main__':
	stdout_val, stderr_val = external_cmd('find . -name *.wav   | wc -l')
#	print 'Standard Output: %s' % stdout_val
#	print 'Standard Error: %s' % stderr_val
#	info=os.system('find . -name *.wav   | wc -l')
	value = int(stdout_val)
	print value
#	print 'os.system', info
	exit(value)