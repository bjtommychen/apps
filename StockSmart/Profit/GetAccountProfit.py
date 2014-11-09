import sys
import os
import socket
import math
import csv
import stat,fnmatch
import struct
import pandas

# reload(sys) 
# sys.setdefaultencoding('utf')

def getFileList(path, ext, subdir = True ):
    if os.path.exists(path):
        dirlist = []
    
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
#            print fullname
            st = os.lstat(fullname)
            if stat.S_ISDIR(st.st_mode) and subdir:
                dirlist += getFileList(fullname,ext)
            elif os.path.isfile(fullname):
                if fnmatch.fnmatch( fullname, ext): 
                    dirlist.append(fullname)
                else:
                    pass
        return dirlist
    else:
        return [] 
        
def GetDataFrame_FromFiles(csvlist):
    filelist = []
    column_names = ['name','date','time','flag','price','count','amount','cjbh','wtbh','zqdm','gddm']
    for one in csvlist:
        if 'tommy' in one:
        # if 'xibao' in one:
            filelist.append(one)
    print filelist
    df = pandas.DataFrame()
    for one in filelist:
        df_tmp = pandas.read_csv(one, names=column_names)
        # print len(df_tmp)
        df = df.append(df_tmp[1:], ignore_index = True)
    df = df.sort(['zqdm', 'date'])
    df = df[['name','date','time','flag','price','count','amount', 'zqdm']]
    df = df.replace('买入'.decode('utf').encode('gbk'), 'buy')
    df = df.replace('卖出'.decode('utf').encode('gbk'), 'sell')
    df = df.replace('申购新股'.decode('utf').encode('gbk'), 'new')
    # print df.head(20)
    # print df.tail(20)
    # for i in range(len(df.columns)):
        # print i, df.columns[i]
    print df.describe()
    return df
      
def CalculateProfit(df):
    print 'Total', len(df)
    name2check = ''
    code2check = 0
    lastprice = 0
    profit = 0
    TotalProfit = 0
    trade_count = 0
    newstock_failed = 0
    newstock_hit = 0
    newstock_profit = 0
    newstock = False
    newstock_name = ''
    newstock_list = []
    for i in range(len(df)):
        name = df.iloc[i]['name']
        date = df.iloc[i]['date']
        time = df.iloc[i]['time']
        flag = df.iloc[i]['flag']
        price = float(df.iloc[i]['price'])
        count = int(df.iloc[i]['count'])
        amount = float(df.iloc[i]['amount'])
        code = int(df.iloc[i]['zqdm'])
        if code2check != code:  #NEW
            print '\t\t', 'Profit:', profit, 'Count_balance:', trade_count
            # if trade_count > 0:
                # print 'Adjust start.', lastprice, trade_count
                # profit += lastprice * trade_count
                # trade_count = 0
                # print '\t\t', 'Profit:', profit, 'Count_balance:', trade_count
            
            if trade_count == 0:
                TotalProfit += profit
            if trade_count == 0 and profit == 0:
                newstock_failed += 1
            if profit > 0 and newstock:
                newstock_hit += 1
                newstock_profit += profit
                newstock_list.append(newstock_name+str(profit))
            print 'TotalProfit', TotalProfit    
            profit = 0; trade_count = 0; newstock = False
            code2check = code
            print 'Check:', name
        print '\t', date,time,flag,price,count,amount
        if name == '申购款'.decode('utf').encode('gbk'):
            continue
        if name.find('GC00') != -1 or name.find('招商银行'.decode('utf').encode('gbk')) != -1:
            continue
        if flag == 'new':
            newstock = True
            newstock_name = name
        if (flag == 'buy' or flag == 'new') and amount > 0:
            trade_count += count
            profit -= amount
        elif flag == 'sell':
            trade_count -= count
            profit += amount
        lastprice = price
    print '\t\t', 'Profit:', profit, 'Count_balance:', trade_count            
        # print (df.iloc[i]['name'])
    print 'Result:'
    print 'newstock_failed', newstock_failed
    print 'newstock_hit', newstock_hit
    for i in range(len(newstock_list)):
        print '\t', i, newstock_list[i]
    print 'newstock_profit', newstock_profit
    print 'TotalProfit', TotalProfit
    
if  __name__ == '__main__':
    print '#'*60
    print '##### Get Account Profit from csv file list.'
    print '#'*60           
    df = GetDataFrame_FromFiles(getFileList('./', '*.csv', False))
    CalculateProfit(df)