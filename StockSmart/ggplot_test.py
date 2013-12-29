
import time
from ggplot import *
from pandas import DataFrame, Timestamp
import datetime
import numpy as np


def info_meat():
    print meat
    print len(meat)

    if False:
        items = len(meat)
        for i in xrange(items):
            for j in meat:
                print meat[j][i],',',
            print 

    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    print meat_lng
    if False:
        items = len(meat_lng)
        for i in xrange(items):
            for j in meat_lng:
                print meat_lng[j][i],',',
            print
    
#     for date, variable, value in meat_lng[][2].items():
#         print date, variable, value
    print 'plot done'

power_data = [[  4.13877565e+04,   2.34652000e-01],
                [  4.13877565e+04,   2.36125000e-01],
                [  4.13877565e+04,   2.34772000e-01],
                [  4.13882896e+04,   2.29006000e-01],
                [  4.13882896e+04,   2.29019000e-01],
                [  4.13882896e+04,   2.28404000e-01]]

def test1():
    powd = DataFrame(power_data, columns=['TIME', 'Watts'])
    print ggplot(aes(x='TIME', y='Watts'), data=powd) + \
        geom_point(color='lightblue') + \
        geom_line(alpha=0.25) + \
        stat_smooth(span=.05, color='black') + \
        ggtitle("Power comnsuption over 13 hours") + \
        xlab("Time") + \
        ylab("Watts")    

def test2():
    d = 1185877080
    print time.gmtime(d)
    print type(time.gmtime(d))
    print time.strftime('%Y--%m--%d %H:%M:%S', time.gmtime(d))
    dt = datetime.datetime(time.gmtime(d).tm_year, time.gmtime(d).tm_mon, time.gmtime(d).tm_mday, 
                           time.gmtime(d).tm_hour, time.gmtime(d).tm_min, time.gmtime(d).tm_sec, 0)
    print dt, type(dt)
    dt64 = np.datetime64(dt)
    print dt64, type(dt64)
    
    ts = Timestamp(dt64)
    print ts, type(ts)

if  __name__ == '__main__':
    test2()
    