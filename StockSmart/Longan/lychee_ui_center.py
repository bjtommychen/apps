 # -*- coding: utf-8 -*
import os
import sys, time
from select import select
import platform

from lychee_sys import *
from lychee_gtalk import *
from lychee_gtalk_io import *
from lychee_eyeonme import *

### config
ui_use_gtalk_io = True         # If False, use print, not gtalk.

### constants
ui_running = True
ui_gtalk_newcmd_got = False
ui_gtalk_newcmd = ''

ui_force_update = False

ui_help_str = 'Main Menu:\n'+ \
            '\thelp - print this help.\n'+ \
            '\tui - control ui.\n'+ \
            '\tsys - system info.\n'+ \
            '\tgtalk - control gtalk.\n'+ \
            '\tupdate - update by force.\n'


def ui_gtalk_messageCB(contex, msg):
    if msg.getBody():
        #msgbody = msg.getBody() #.decode('gbk'))
        #print ("Sender: " + str(msg.getFrom()))
        #print ("Content: " + str(msg.getBody()))
        #text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + '\n'
            
        #who = msg.getFrom().getStripped()
        #if "chen.tao.tommy" in who:
        #    contex.send(xmpp.Message(msg.getFrom(), (msg.getBody()), typ = 'chat'))
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
    
if platform.system() == "Windows":
    import msvcrt

def input_with_timeout_sane(prompt, timeout, default):
    """Read an input from the user or timeout"""
    print prompt,
    sys.stdout.flush()
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
        s = sys.stdin.readline().replace('\n','')
    else:
        s = default
        print s
    return s

def input_with_timeout_windows(prompt, timeout, default): 
    start_time = time.time()
    print prompt,
    sys.stdout.flush()
    input = ''
    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getche()
            if ord(chr) == 13: # enter_key
                break
            elif ord(chr) >= 32: #space_char
                input += chr
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break
    if len(input) > 0:
        return input
    else:
        return default

def input_with_timeout(prompt, timeout, default=''):
    if platform.system() == "Windows":
        return input_with_timeout_windows(prompt, timeout, default)
    else:
        return input_with_timeout_sane(prompt, timeout, default)    
    
def ui_get_commands():
    str = []
    if not ui_use_gtalk_io:
        #str = raw_input('Please input cmds .... ')
        str = input_with_timeout('<input>', 5)
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
    strout = ''
    if (len(cmds) < 1):
        return
    elif cmds[0] == 'help' or cmds[0] == '?':
        strout += ui_help_str
    elif cmds[0] == 'update':
        global ui_force_update
        ui_force_update = True
        strout += 'Force update ' + str(ui_force_update)
    elif cmds[0] == 'ui':
        strout += ui_process_ui_cmds(cmds[1:])
    elif cmds[0] == 'sys':
        strout += sys_process_cmds(cmds[1:])
    elif cmds[0] == 'gtalk':
        strout += gtalk_process_cmds(cmds[1:])        
    # elif cmds[0] == 'stockmon':
        # strout += stockmon_process_cmds(cmds[1:])        
    else:
        strout += 'invalid command'
    return strout
        
def ui_put_str(string):
    global ui_running
    # print 'ui_running', ui_running
    if len(string) >0:
        if ui_use_gtalk_io:
            Gtalk_send(string)
        else:
            print '[OUTPUT]\n', string
    return

def ui_init():
    # choose IO 
    if ui_use_gtalk_io:
        Gtalk_init(ui_gtalk_messageCB)
        Gtalk_run()
    ui_put_str('******  ui_init  ******')
    ui_put_str(time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + '\n')
    strout = ''
    # strout += webdrv_init()
    strout += stockmon_init()
    # strout += crawler_init()   
    ui_put_str(strout)
    
def ui_exit():   
    strout = ''
    # strout += webdrv_exit()
    # strout += stockmon_exit()
    # strout += crawler_exit()   
    ui_put_str(strout)
    
def ui_reboot_to_refresh():
    checkopen = False
#    if (datetime.datetime.now().weekday() > 4):
#        return False
    text = time.strftime("%H:%M", time.localtime())
    if text == '09:00' or text == '21:25' or text == '19:50':
        checkopen = True
    return checkopen    
    
def ui_mainloop():
    global ui_running
    global ui_force_update
    
    ui_init()
    while(ui_running):
        print '@1',
        if ui_reboot_to_refresh():
            time.sleep(60)
            ui_running = False
        cmds = ui_get_commands()
        print '@2',
        if len(cmds)>0:
            #print '[INPUT]:', cmds
            output = ui_dispatch_commands(cmds)
            ui_put_str(output)
        print '@3\r------',
        try:
            output = stockmon_process(ui_force_update)
            if ui_force_update:
                ui_force_update = False
            ui_put_str(output)
            time.sleep(1)
        except:
            print 'ui main loop except!'
            ui_running = False         
    ui_put_str('ui_mainloop done.')
    ui_exit()
    if ui_use_gtalk_io:
        Gtalk_exit()
