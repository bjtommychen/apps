#! /usr/bin/env python
# encoding=UTF-8

import xmpp
import time
import sys
import thread

# Global
gtalk_running = True
conn = 0
enable_send = True

# Strings
string_help = 'Help commands:\n Supported commands: exit, help.\n'

# Debug
def log_d(string):
    if True:
        print string

def log_i(string):
    if True:
        print string
        
# Msg call back
def messageCB(contex, msg):
#     if contex.Process(1) == None:
#         return
    if msg.getBody():
        log_d ("Sender: " + str(msg.getFrom()))
        log_d ("Content: " + str(msg.getBody()))
        text = ''
        text += time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime()) + '\n'
        if (msg.getBody() == 'exit'):
            global gtalk_running
            gtalk_running = False
            text += 'Bye!'
        elif (msg.getBody() == 'help'):
            text = string_help
        else:
            text += str(msg.getBody())
        contex.send(xmpp.Message(str(msg.getFrom()), text, typ = 'chat'))

def presenceHandler(contex, presence):
    if presence:
        print "-"*100
        print presence.getFrom(), ",", presence.getFrom().getResource(), ",", presence.getType(), ",", presence.getStatus(), ",", presence.getShow()
        print "~"*100
        if presence.getType()=='subscribe':
            jid = presence.getFrom().getStripped()
            """ Authorise JID 'jid'. Works only if these JID requested auth previously. """
            contex.getRoster().Authorize(jid)
            print 'Authorize'  + jid           
#            self.authorize(jid)

def Gtalk_enable_send(onoff):
    global enable_send
    enable_send = onoff

def Gtalk_send(msg):
    global enable_send
    if enable_send:
        global conn
        if not conn:
            Gtalk_init()
            Gtalk_run()
            time.sleep(2)
        log_d('send msg:' + msg)    
        res = conn.send(xmpp.Message('chen.tao.tommy@gmail.com', msg, typ = 'chat'))
        log_d( 'send ' + res)
    else:
        log_d(msg)

def Gtalk_init():
    global conn
    username = 'tchen1973@gmail.com'
    pwd = 'Happyday310'

    gmail_account = username
    jid=xmpp.JID(gmail_account)
    server = jid.getDomain()
    log_i (jid.getDomain())
    conn = xmpp.Client(server, debug=[])

    # Connect
    log_i ('connect...',)
    conres=conn.connect(('talk.L.google.com',5222))
#    , proxy={'host':'127.0.0.1','port':8087,})
    log_i ('done')
    log_d (conres)
    
    if not conres:
        log_d ("Unable to connect to server %s!" %server)
        sys.exit(1)
    if conres<>'tls':
        log_d ("Warning: unable to estabilish secure connection - TLS failed!")
    
    # Auth
    log_i ('auth...' + jid.getNode())
    authres = conn.auth(jid.getNode(), pwd)
    log_i ('done')

    if not authres:
        log_d ("Unable to authorize on %s - Plsese check your name/password."%server)
        sys.exit(1)
    if authres<>"sasl":
        log_d ("Warning: unable to perform SASL auth os %s. Old authentication method used!"%server)    
    
    # Send roster request and initial
    log_d ('sendInitPresence')
    conn.sendInitPresence()
    # Register Callback
    log_d ('registerHandler')
    conn.RegisterHandler('message', messageCB)
    conn.RegisterHandler('presence', presenceHandler)
    
def Gtalk_run():
    thread.start_new_thread(gtalk_mainloop, ())
    time.sleep(1)
    Gtalk_send('Gtalk robot v1.0 ---> online!')
    Gtalk_send('Welcome Tommy:)')
    
def gtalk_mainloop():    
    global conn
    global gtalk_running    
    log_i ('Enter Gtalk main loop ................................')
    while gtalk_running:
        if conn.Process(1) == None:
            log_d ('Lost connection.')
            conn = 0
            break
        if not gtalk_running:
            log_d ('Exit Gtalk main loop !!!!!!!!!!!!!!!!!!')
            break;
#        log_d ('gtalk_running:' + str(gtalk_running))
        print '$',
        time.sleep(1)
    log_i ('gtalk_mainloop Done!')
    gtalk_running = False
    if conn:
        conn.disconnect()
        conn = 0

def Gtalk_exit():
    global gtalk_running
    global conn
    if conn:
        conn.disconnect()
        conn = 0
    gtalk_running = False
    
def Gtalk_isRunning():
    global gtalk_running
    return gtalk_running    
    
if __name__ == '__main__':    
    print "Main"
    Gtalk_init()
    Gtalk_run()
    Gtalk_send('Welcome tommy ! I am online! ')
    time.sleep(20)
        