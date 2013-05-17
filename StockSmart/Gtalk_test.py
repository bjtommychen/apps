#! /usr/bin/env python
# encoding=UTF-8

import xmpp
import time
import sys
import thread

running = True
cnx = 0

string_help = 'Help commands:\n Supported commands: exit, help.\n'


#debug
def log_d(string):
    if True:
        print string

def log_i(string):
    if True:
        print string
        
# 消息回调函数
def messageCB(cnx, msg):
    # 显示消息发送者和内容
    if msg.getBody():
        log_d ("Sender: " + str(msg.getFrom()))
        log_d ("Content: " + str(msg.getBody()))
        # 将消息又返回给发送者
        if (msg.getBody() == 'exit'):
            global running
            running = False
            cnx.send(xmpp.Message(str(msg.getFrom()), 'Bye!', typ = 'chat'))
#            sys.exit(0)
        elif (msg.getBody() == 'help'):
            cnx.send(xmpp.Message(str(msg.getFrom()), string_help, typ = 'chat'))
        else:
            cnx.send(xmpp.Message(str(msg.getFrom()), str(msg.getBody()), typ = 'chat'))

def Gtalk_send(msg):
    global cnx
    if not cnx:
        Gtalk_init()
        Gtalk_run()
        time.sleep(1)
    log_d('send msg:' + msg)    
    res = cnx.send(xmpp.Message('chen.tao.tommy@gmail.com/Talk.v1040ADDDBD8', msg, typ = 'chat'))
    print 'send' + res

def Gtalk_init():
    global cnx
    # 给实例的gtalk帐号和密码
    username = 'tchen1973@gmail.com'
    pwd = 'Happyday310'
    # 创建client对象
    gmail_account = username
    jid=xmpp.JID(gmail_account)
    server = jid.getDomain()
    log_i (jid.getDomain())
    cnx = xmpp.Client(server, debug=[])
    # 连接到google的服务器
    log_i ('connect...',)
    conres=cnx.connect(('talk.L.google.com',5222))
#    , proxy={'host':'127.0.0.1','port':8087,})
    log_i ('done')
    log_d (conres)
    
    if not conres:
        log_d ("Unable to connect to server %s!" %server)
        sys.exit(1)
    if conres<>'tls':
        log_d ("Warning: unable to estabilish secure connection - TLS failed!")
    
    # 用户身份认证
    log_i ('auth...' + jid.getNode())
    authres = cnx.auth(jid.getNode(), pwd)
    log_i ('done')

    if not authres:
        log_d ("Unable to authorize on %s - Plsese check your name/password."%server)
        sys.exit(1)
    if authres<>"sasl":
        log_d ("Warning: unable to perform SASL auth os %s. Old authentication method used!"%server)    
    
    # 告诉gtalk服务器用户已经上线
    log_d ('sendInitPresence')
    cnx.sendInitPresence()
    # 设置消息回调函数
    log_d ('registerHandler')
    cnx.RegisterHandler('message', messageCB)
    
def Gtalk_run():
    log_d('Gtalk_run start.')
    thread.start_new_thread(gtalk_mainloop, ())
    log_d('Gtalk_run done.')
    
def gtalk_mainloop():    
    global cnx    
    log_i ('Enter main loop ................................')
    # 循环处理消息,如果网络断开则结束循环
    while True:
        if cnx.Process(1) == None:
            log_d ('Lost connection.')
            break
        if not running:
            log_d ('Exit !!!!!!!!!!!!!!!!!!')
            break;
#        log_d ('running:' + str(running))
        print '$',
        time.sleep(1)
    log_i ('gtalk_mainloop Done!')
    
    
if __name__ == '__main__':    
    print "Main"
    Gtalk_init()
    Gtalk_run()
    time.sleep(5)
    print 'try send'
    Gtalk_send('Welcome tommy ! I am online! ')
        