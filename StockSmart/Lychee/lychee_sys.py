# -*- coding: utf-8 -*
import time
import sys
import os

def sys_process_cmds(cmds):
    print 'sys_process_cmds', cmds
    str = ''
    if (len(cmds) == 0):
        str += 'sys help - for more.'
    else:    
        if cmds[0] == 'help' or cmds[0] == '?':
            str += 'sys help:\n'+ \
                '\thelp - print help \n'
    return str