import time
import sys
import os
import socket
import math
import csv
import stat,fnmatch
import subprocess
import multiprocessing

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

MAX_PROCESSING = 4    
def run_cmdline_processing(q, lock, cmdline):
    # print 'run_cmdline_processing', onefile
    try:
        external_cmd(cmdline)
    except:
        print 'error'
        
def do_multiprocessing(cmdlines):
    global MAX_PROCESSING
    global result_logs
    cnt = 0
    runcnt = 0
    p_list = []
    print 'multiprocessing.cpu_count()', multiprocessing.cpu_count()
    q = multiprocessing.Queue()
    q.put([])
    lock = multiprocessing.Lock()
    for line in cmdlines:
        cnt += 1
        print (' Processing No.'+str(cnt)+'/'+str(len(cmdlines))).center(79, '-')
        print line
        p = multiprocessing.Process(target=run_cmdline_processing, args=(q, lock, line))
        p.start()
        p_list.append(p)
        # print p,'added'
        time.sleep(0.2)
        while(len(p_list) >= MAX_PROCESSING):
            print 'Waiting ...'
            time.sleep(2)
            for p in p_list:
                # print p
                p.join(timeout=0.1)
                if not p.is_alive():
                    p_list.remove(p)
                    # handle_ResultsInQueue(q.get())
                    # print 'Removing Process', p
    for p in p_list:
        # print 'wait join', p
        p.join()
        # handle_ResultsInQueue(q.get())
    result_logs = q.get()
    print 'result_logs', len(result_logs), result_logs
    print 'All Done!'        
        
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
        
def Save2PNG_OneList(fname_list, fname_png_prefix, save_path = './save_png/', withDate = False):
    if not os.path.exists(fname_list):
        return
    filename  = csv_path+fname_list
    reader = csv.reader(file(filename,'rb'))
    i = 0
    cmdlists = []
    for one in reader:
        if len(one) < 2:
            continue
        code = one[1]
        name = ''
        if '_cn' in fname_list or 'cn_' in fname_list:
            name = GetCodeName_cn(code)
        elif '_hk' in fname_list:
            name = GetCodeName_hk(code)
        elif '_us' in fname_list:
            name = GetCodeName_us(code)
        if not withDate:
            cmdline = 'GetFollowsChangesByName_db.py -t ' + str(code) + ' --save ' + save_path+ fname_png_prefix + '%02d_'%i+code+name+'.png'
        else:
            timetext = time.strftime("%Y%m%d", time.localtime()) 
            cmdline = 'GetFollowsChangesByName_db.py -t ' + str(code) + ' --save ' + save_path+timetext+'_'+ fname_png_prefix + '%02d_'%i+code+name+'.png'
        cmdlists.append(cmdline)
        i+= 1  
    if False:        
        for cmdline in cmdlists:
            print cmdline
            external_cmd(cmdline)        
    else:
        do_multiprocessing(cmdlists)
        
        
if  __name__ == '__main__':
    print '#'*60
    print '##### Convert Watch List to PNG files.'
    print '#'*60

    if True:
        Save2PNG_OneList('hold_cn.csv', 'cn_H', './save_png/', True)
        Save2PNG_OneList('watch_cn.csv', 'cn_W', './save_png/', True)
        Save2PNG_OneList('Sideway_cn.csv', 'cn_sideway', './save_png/sideway/', True)
        Save2PNG_OneList('catchspurt_cn.csv', 'cn_CatchSpurt', './save_png/catchspurt/', True)
    
    if True:
        Save2PNG_OneList('cn_spurt_today.csv', 'cn_spurt', './save_png/spurt/', True)

    if True: #low priority
        Save2PNG_OneList('hold_hk.csv', 'hk_H', './save_png/', True)
        Save2PNG_OneList('watch_hk.csv', 'hk_W', './save_png/', True)
        Save2PNG_OneList('hold_us.csv', 'us_H', './save_png/', True)
        Save2PNG_OneList('watch_us.csv', 'us_W', './save_png/', True)
    
    print 'Done'