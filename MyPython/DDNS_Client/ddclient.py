import os
import urllib2
import urllib
import sys

#用来激活花生壳
if __name__ == '__main__':
    print 'Connecting ddns server...'
    str=urllib.urlopen("http://bj:ha@ddns.oray.com/ph/update?hostname=bj.oicp.net").read()
    print 'Result: urlopen done, read done.'
    print '*'*20
    print str
    print '*'*20
    print 'Done.'