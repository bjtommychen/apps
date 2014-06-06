# -*- coding: utf-8 -*
import time
import sys
import os

def dev_process_cmds(cmds):
    print 'dev_process_cmds', cmds
    str = ''
    if (len(cmds) == 0):
        str += 'dev help - for more.'
    else:    
        if cmds[0] == 'help' or cmds[0] == '?':
            str += 'dev help:\n'+ \
                '\thelp - print help \n'
    return str