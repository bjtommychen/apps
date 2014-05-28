import sys
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print 'System Default Encoding:',sys.getdefaultencoding()
reload(sys) 
#sys.setdefaultencoding('utf8')
sys.setdefaultencoding('gbk')   #Tommy: this make IPthon display chinese OK.

def test_example():
    x = np.linspace(0, 2*np.pi, 50)
    y = np.sin(x)
    y2 = y + 0.1 * np.random.normal(size=x.shape)
    print type(x), type(y),len(x), len(y)
    print list(x)
    fig, ax = plt.subplots()
    ax.plot(x, y, 'k--')
    ax.plot(x, y2, 'ro')
    plt.show()

def plot0():
    filepath=unicode("e:\\bigdata\\doc\\data0.csv",'utf8')
    df = pd.read_csv(filepath, skiprows=[0])
    # print df
    # print df.head()
    # print df.tail()
    #s = df['total_days']
    #s.hist(normed=True, alpha=0.2);s.plot(kind='kde', title='aa');plt.show()
    #fig, ax = plt.subplots();ax.plot(s,'.');plt.show()
    #df[df.total_days>500].sort(columns='success_pct').tail()
    #df[(df.total_days>500) & (df.success_pct>1)].sort(columns='failed_pct').tail(20)

    #tommy: so use this
    #df[(df.total_days>500)&(df.success_pct>3)].sort(columns='failed_pct').head(10)
    plt.show()
    
def plot1():
    
    
if  __name__ == '__main__':
    plot0()
    print 'done'