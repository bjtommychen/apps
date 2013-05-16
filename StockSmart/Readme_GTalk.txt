

D:\Python27\Scripts>easy_install xmpppy

http://guangboo.org/2013/02/25/xmpp-communication-implement-with-xmpppy


上面问题解决，双方帐号认证后就可互相发送信息了。用以下命令向jims.yang@gmail.com申请认证。

>;>;>;c.Roster.Subscribe('jims.yang@gmail.com')

在google的Open Communications 上获得以下信息：
The service is hosted at talk.google.com on port 5222 
TLS is required 
The only supported authentication mechanism is SASL PLAIN 