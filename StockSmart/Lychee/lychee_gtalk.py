# -*- coding: utf-8 -*
import time
import sys
import os
from lychee_gtalk_io import *

def gtalk_process_cmds(cmds):
    print 'gtalk_process_cmds', cmds
    str = ''
    if (len(cmds) == 0):
        str += 'gtalk help - for more.'
    else:    
        if cmds[0] == 'help' or cmds[0] == '?':
            str += 'gtalk help:\n'+ \
                '\thelp - print help \n'+\
                '\ton - gtalk on \n' +\
                '\toff - gtalk off \n' +\
                ''
        if cmds[0] == 'on':
            Gtalk_enable_send(True)
            str += 'Gtalk set on.'
        if cmds[0] == 'off':
            Gtalk_enable_send(False)
            str += 'Gtalk set off.'
            
    return str