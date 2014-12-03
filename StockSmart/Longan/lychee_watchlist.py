import os, sys, time
import string
import stat,fnmatch
import datetime
import csv

filelist = [['watch_cn.csv', ''], ['watch_hk.csv', ''], ['watch_us.csv', ''], ['hold_cn.csv', ''], ['hold_hk.csv', ''], ['hold_us.csv', ''],]

def watchlist_update():
    DataPath = './'
    files = os.listdir(DataPath)
    bChanged = False
    for i in range(0, len(filelist)):
        # print 'Checking', filelist[i][0]
        if os.path.exists(os.path.join(DataPath, filelist[i][0])) == False and filelist[i][1] != '':
            print filelist[i][0],'removed.'
            filelist[i][1] = ''
            bChanged = True
            break            
        for file in files:
            if fnmatch.fnmatch(file, filelist[i][0]):  
                fileName = os.path.join(DataPath, file)  
                filemt = time.localtime(os.stat(fileName).st_mtime)  
                filetime = datetime.datetime( filemt[0] ,filemt[1] ,filemt[2], filemt[3], filemt[4], filemt[5]) 
                if filelist[i][1] == '' or filelist[i][1] != filetime:
                    print filelist[i][0],'changed.'
                    filelist[i][1] = filetime
                    bChanged = True
                    break
    if bChanged:
        time.sleep(10)  #Wait until all watch list file copied.   
        return watchlist_load()
    else:
        return []

def watchlist_load():
    listall = []
    for i in range(0, len(filelist)):
        name = filelist[i][0]
        if os.path.exists(name):
            reader = csv.reader(file(name,'rb'))    
            for row in reader:
                listall.append(row)
    return listall
    
#############################################    
if  __name__ == '__main__':
    for i in range(0, 22):
        print watchlist_update()
        time.sleep(10)
