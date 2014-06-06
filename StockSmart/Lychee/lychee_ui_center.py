 # -*- coding: utf-8 -*
import time
import sys
import os

from lychee_dev import *
from lychee_sys import *
from lychee_gtalk import *
from lychee_gtalk_io import *

### constants
ui_running = True
ui_use_gtalk_io = False
ui_gtalk_newcmd_got = False
ui_gtalk_newcmd = ''

ui_help_str = 'Main Menu:\n'+ \
            '\thelp - print this help.\n'+ \
            '\tui - control ui.\n'+ \
            '\tsys - system info.\n'+ \
            '\tgtalk - control gtalk.\n'+ \
            '\tmore - print this help.\n'+ \
            '\tdev - for dev only.\n'


def ui_gtalk_messageCB(contex, msg):
    if msg.getBody():
        #msgbody = msg.getBody() #.decode('gbk'))
        #print ("Sender: " + str(msg.getFrom()))
        #print ("Content: " + str(msg.getBody()))
        #text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + '\n'
            
        who = msg.getFrom().getStripped()
        if "chen.tao.tommy" in who:
            contex.send(xmpp.Message(msg.getFrom(), (msg.getBody()), typ = 'chat'))
        global ui_gtalk_newcmd, ui_gtalk_newcmd_got
        ui_gtalk_newcmd = msg.getBody()
        ui_gtalk_newcmd_got = True

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
    str = []
    if not ui_use_gtalk_io:
        str = raw_input('Please input cmds .... ')
        str = str.split()
    else:
        global ui_gtalk_newcmd, ui_gtalk_newcmd_got
        if ui_gtalk_newcmd_got:
            ui_gtalk_newcmd_got = False
            str = ui_gtalk_newcmd
            str = str.split()
    return str

#DISPATCH    
def ui_dispatch_commands(cmds):
    print '\nui_dispatch_commands', cmds
    output = ''
    if (len(cmds) < 1):
        return
    if cmds[0] == 'help' or cmds[0] == '?':
        output += ui_help_str
    if cmds[0] == 'ui':
        output += ui_process_ui_cmds(cmds[1:])
    if cmds[0] == 'dev':
        output += dev_process_cmds(cmds[1:])
    if cmds[0] == 'sys':
        output += sys_process_cmds(cmds[1:])
    if cmds[0] == 'gtalk':
        output += gtalk_process_cmds(cmds[1:])        
    return output
        
def ui_put_str(string):
    if len(string) >0:
        if ui_use_gtalk_io:
            Gtalk_send(string)
        else:
            print '[OUTPUT]\n', string
    return

def ui_mainloop():
    # choose IO 
    if ui_use_gtalk_io:
        Gtalk_init(ui_gtalk_messageCB)
        Gtalk_run()
    ui_put_str('Lychee Mainloop start.')
    ui_put_str(time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + '\n')
    while(ui_running):
        cmds = ui_get_commands()
        if len(cmds)>0:
            #print '[INPUT]:', cmds
            output = ui_dispatch_commands(cmds)
            ui_put_str(output)
        print '.',
        time.sleep(0.5)
    ui_put_str('ui_mainloop done.')
    if ui_use_gtalk_io:
        Gtalk_exit()
