
import time
from ggplot import *
from pandas import DataFrame, Timestamp
import datetime
import numpy as np

# <class 'pandas.core.frame.DataFrame'>
# Int64Index: 827 entries, 0 to 826
# Data columns (total 8 columns):
# date               827  non-null values
# beef               827  non-null values
# veal               827  non-null values
# pork               827  non-null values
# lamb_and_mutton    827  non-null values
# broilers           635  non-null values
# other_chicken      143  non-null values
# turkey             635  non-null values
# dtypes: datetime64[ns](1), float64(7)

def info_meat():
    print meat
    print len(meat)
    print '---'

    if False:
        items = len(meat)
        for i in xrange(items):
            for j in meat:
                print meat[j][i],',',
            print 
    print '---'
    
    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    print meat_lng
    if False:
        items = len(meat_lng)
        for i in xrange(items):
            for j in meat_lng:
                print meat_lng[j][i],',',
            print
    print '---'    
    print meat[['date', 'beef','pork']]
    print pd.melt(meat[['date', 'beef','pork']])
    print pd.melt(meat[['date', 'beef','pork']], id_vars='date')
#     for date, variable, value in meat_lng.items():
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

def test3():
    meat_lng = pd.melt(meat, id_vars=['date'])
    p = ggplot(aes(x='date', y='value'), data=meat_lng)
    p += geom_point(color='lightblue') 
    p += stat_smooth(span=.05,colour="red") 
    p += facet_wrap("variable")
    print p     

def test4():
    sd = pd.read_csv('data/600845.csv')
    print sd
    print len(sd)
    if True:
        items = len(sd)
        for i in xrange(items):
            for j in sd:
                print sd[j]['Open'],',',
        print 'done'
    print ggplot(aes(x='High', y='Open'), data=sd) + \
        geom_point(color='lightblue') + \
        geom_line(alpha=0.25) + \
        stat_smooth(span=.05, color='black') + \
        ggtitle("Power comnsuption over 13 hours") + \
        xlab("Time") + \
        ylab("Watts")    

if  __name__ == '__main__':
    info_meat()
#     test4()
#     test1()
    