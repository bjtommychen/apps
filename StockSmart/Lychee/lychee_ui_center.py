 # -*- coding: utf-8 -*
import time
import sys
import os

from lychee_dev import *

ui_running = True
ui_help_str = 'Main Menu:\n'+ \
            '\thelp - print this help.\n'+ \
            '\tui - control ui.\n'+ \
            '\tsys - system info.\n'+ \
            '\tgtalk - control gtalk.\n'+ \
            '\tmore - print this help.\n'+ \
            '\tdev - for dev only.\n'


def ui_process_ui_cmds(cmds):
    print 'ui_process_ui_cmds', cmds
    str = ''
    if (len(cmds) == 0):
        str += 'ui help - for more.'
    else:
        if cmds[0] == 'help' or cmds[0] == '?':
            str += 'ui help:\n'+ \
                '\thelp - print this help.\n'+ \
                '\texit - exit ui system.\n'
        if cmds[0] == 'exit':
            global ui_running
            ui_running = False
            str += 'ui system down!\n'
    
    return str
    
def ui_get_commands():
    str = raw_input('Please input cmds .... ')
    str = str.split()
    return str

def ui_dispatch_commands(cmds):
    print 'ui_dispatch_commands', cmds
    output = ''
    if (len(cmds) < 1):
        return
    if cmds[0] == 'help' or cmds[0] == '?':
        output += ui_help_str
    if cmds[0] == 'ui':
        output += ui_process_ui_cmds(cmds[1:])
    if cmds[0] == 'dev':
        output += dev_process_cmds(cmds[1:])
    return output
        
def ui_put_str(string):
    if len(string) >0:
        print '[OUTPUT]\n', string

def ui_mainloop():
    ui_put_str('ui_mainloop start.')
    while(ui_running):
        cmds = ui_get_commands()
        if len(cmds)>0:
            print '[INPUT]:', cmds
            output = ui_dispatch_commands(cmds)
            ui_put_str(output)
        
        time.sleep(1)
    ui_put_str('ui_mainloop done.')
