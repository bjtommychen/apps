#! /usr/bin/env python
# encoding=UTF-8

import xmpp
import time
import sys

running = True

# 消息回调函数
def messageCB(cnx, msg):
    # 显示消息发送者和内容
    if msg.getBody():
        print "Sender: " + str(msg.getFrom())
        print "Content: " + str(msg.getBody())
        # 将消息又返回给发送者
        cnx.send(xmpp.Message(str(msg.getFrom()), str(msg.getBody()), typ = 'chat'))
        if (msg.getBody() == 'exit'):
            global running
            running = False
#            sys.exit(0)
        elif (msg.getBody() == 'help'):
            cnx.send(xmpp.Message(str(msg.getFrom()), 'Help commands: exit, help.', typ = 'chat'))

if __name__ == '__main__':
    # 给实例的gtalk帐号和密码
    username = 'tchen1973@gmail.com'
    pwd = 'Happyday310'
    # 创建client对象
    gmail_account = username
    jid=xmpp.JID(gmail_account)
    server = jid.getDomain()
    print jid.getDomain()
    cnx = xmpp.Client(server, debug=[])
    # 连接到google的服务器
    print 'connect...',
    conres=cnx.connect(('talk.L.google.com',5222))
#    , proxy={'host':'127.0.0.1','port':8087,})
    print 'done'
    print conres
    
    if not conres:
        print "Unable to connect to server %s!" %server
        sys.exit(1)
    if conres<>'tls':
        print "Warning: unable to estabilish secure connection - TLS failed!"
    
    # 用户身份认证
    print 'auth...', jid.getNode()
    authres = cnx.auth(jid.getNode(), pwd)
    print 'done'

    if not authres:
        print "Unable to authorize on %s - Plsese check your name/password."%server
        sys.exit(1)
    if authres<>"sasl":
        print "Warning: unable to perform SASL auth os %s. Old authentication method used!"%server    
    
    # 告诉gtalk服务器用户已经上线
    print 'sendInitPresence'
    cnx.sendInitPresence()
    # 设置消息回调函数
    print 'registerHandler'
    cnx.RegisterHandler('message', messageCB)
    print 'Enter main loop ................................'
    # 循环处理消息,如果网络断开则结束循环
    while True:
        if cnx.Process(1) == None:
            print 'Lost connection.'
            break
        if not running:
            print 'Exit !!!!!!!!!!!!!!!!!!'
            break;
        time.sleep(1)
        print 'running:', running
        
    print 'Done!'
    
    
    
        