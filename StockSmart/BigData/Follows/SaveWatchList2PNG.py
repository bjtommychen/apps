import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import subprocess

save_path = './save_png/'
csv_path = ''  #e:\\KuaiDisk\\StockSmart\\follows\\
    
def save2csv(fname, list):
    fcsv = open(fname, 'wb')
    csvWriter = csv.writer(fcsv)
    csvWriter.writerows(list)
    fcsv.close()
        
def loadfromecsv(fname):
    list = []
    reader = csv.reader(file(fname,'rb'))
    for line in reader:        
        list.append(line)
    return list
    
def external_cmd(cmd, rundir='./', msg_in=''):
    # print 'rundir:',rundir, ', cmds:', cmd
    # return 'stdout', 'stderr'
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   cwd=rundir
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        # time.sleep(0.2)
        return stdout_value, stderr_value
    except ValueError as err:
        print ("ValueError: %s" % err)
        return None, None
    except IOError as err:
        print("IOError: %s" % err)
        return None, None

list_stock_cn = []        
def GetCodeName_cn(code):
    global list_stock_cn
    if list_stock_cn == []:
        list_stock_cn = loadfromecsv('stockinfo_cn.csv')
    first_or_default = next((x for x in list_stock_cn if x[0]==code[2:]), None)
    if first_or_default == None:
        return 'NONAME'
    else:
        return first_or_default[1]

list_stock_hk = []        
def GetCodeName_hk(code):
    global list_stock_hk
    if list_stock_hk == []:
        list_stock_hk = loadfromecsv('stockinfo_hk.csv')
    first_or_default = next((x for x in list_stock_hk if x[0]==code), None)
    if first_or_default == None:
        return 'NONAME'
    else:
        return first_or_default[1]        

list_stock_us = []        
def GetCodeName_us(code):
    global list_stock_us
    if list_stock_us == []:
        list_stock_us = loadfromecsv('stockinfo_us.csv')
    first_or_default = next((x for x in list_stock_us if x[0]==code), None)
    if first_or_default == None:
        return 'NONAME'
    else:
        return first_or_default[1]  
        
def Save2PNG_OneList(fname_list, fname_png_prefix):   
    filename  = csv_path+fname_list
    reader = csv.reader(file(filename,'rb'))
    i = 0
    for one in reader:
        code = one[1]
        name = ''
        if '_cn' in fname_list:
            name = GetCodeName_cn(code)
        elif '_hk' in fname_list:
            name = GetCodeName_hk(code)
        elif '_us' in fname_list:
            name = GetCodeName_us(code)
        cmdline = 'GetFollowsChangesByName.py -t ' + str(code) + ' --save ' + save_path+ fname_png_prefix + '%02d_'%i+code+name+'.png'
        print cmdline
        external_cmd(cmdline)
        i+= 1    
        
if  __name__ == '__main__':
    print '#'*60
    print '##### Convert Watch List to PNG files.'
    print '#'*60

    Save2PNG_OneList('hold_cn.csv', 'cn_HHH')
    Save2PNG_OneList('watch_cn.csv', 'cn_WWW')

    Save2PNG_OneList('hold_hk.csv', 'hk_HHH')
    Save2PNG_OneList('watch_hk.csv', 'hk_WWW')

    Save2PNG_OneList('hold_us.csv', 'us_HHH')
    Save2PNG_OneList('watch_us.csv', 'us_WWW')
    print 'Done'