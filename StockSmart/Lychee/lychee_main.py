 # -*- coding: utf-8 -*
import time
import sys
import os

from lychee_ui_center import *

print 'System Default Encoding:',sys.getdefaultencoding()
#add this to fix crash when Chinsese input under Ubuntu
#reload(sys) 
#sys.setdefaultencoding('utf8')
#sys.setdefaultencoding('gbk')

if  __name__ == '__main__':
    print '#'*60
    print '##### Lychee System. ≤‚ ‘∞Ê' 
    print '#'*60
    print 'Config:'
    
    ui_mainloop()

    print 'Done.'