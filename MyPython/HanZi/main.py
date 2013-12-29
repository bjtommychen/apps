
import time
import sys
import os
import math
import csv
import shutil
import random
import datetime

print 'System Default Encoding:',sys.getdefaultencoding()

#add this to fix crash when Chinsese input under Ubuntu
reload(sys) 
# sys.setdefaultencoding('utf8')

def beep_sos(): 
    sys.stdout.write('\a')

# Handle word2txt file.
def txt2csv1(infile, outfile):
    f = open(infile, 'r')
    fcsv = open(outfile, 'wb')
    csvWriter = csv.writer(fcsv)
    
    i = 0
    for line in f.readlines():
        line = line.strip()
        if (len(line) == 0) or str(line[0]).isdigit()==False or str(line[0:4]) == '2013': 
#             print i, 'line', line
            continue
#         else:
#             continue
        #removing leading digit
        idx = 0
        for idx in range(0, len(line)):
            if str(line[idx]).isdigit():
                continue
            else:
                break
        line = line[idx:].strip()
        #split
        for idx in range(4, len(line)):
            if str(line[idx]).isalnum() or str(line[idx]).isspace():
#             if ord((line[idx])) <127:
                break
        word = line[0:idx].strip()
        comment = line[idx:]
        print i, len(line),'str:',word, 'note::', comment
        wline = i, word, '' , comment
        csvWriter.writerow(wline)
        i+=1
    f.close()
    fcsv.close()                        
             
# Handle pdf2txt file.              
def txt2csv2(infile, outfile):
    f = open(infile, 'r')
    fcsv = open(outfile, 'wb')
    csvWriter = csv.writer(fcsv)
    
    i = 0
    for line in f.readlines():
        line = line.strip()
#         print line
        if (len(line) == 0) or str(line[0]).isdigit()==True or str(line[0:4]) == '2013': 
#             print line
            continue
#         else:
#             print line
#             continue
        idx = 0
#         #split
        for idx in range(0, len(line)):
            if str(line[idx]).isalnum() or str(line[idx]).isspace():
                break
        word = line[0:idx].strip()
        comment = line[idx:].strip()
        print i, len(line),'str:',word, 'note::', comment
        wline = i, word, '' , comment
        csvWriter.writerow(wline)
        i+=1
    f.close()
    fcsv.close()   

def ConvertStr(name):
    try:
        str = name.decode('gbk')
    except:
        str = ''
    return str
                
def check_if_included(file_ref, file_check,outfile):
    rows1 = csv.reader(file(file_check,'rb'))
    rows2 = csv.reader(file(file_ref,'rb'))
    fcsv = open(outfile, 'wb')
    csvWriter = csv.writer(fcsv)    
    total = 0
    cnt_found = 0
    cnt_missed = 0
    for row in rows1:
        total+=1
        name = ConvertStr(row[1])
        comment = ConvertStr(row[3])
        print 'search.....' , name, 
        
        found = False
        idx = 0
        rows2 = csv.reader(file(file_ref,'rb'))
        for checkrow in rows2:
            idx +=1
#             print idx
            checkname = ConvertStr(checkrow[1])
#             print '','',checkname
            if name == checkname:
                found = True
                break
        if found == False:
            cnt_missed +=1
            print 'missed!'
            line = cnt_missed, row[1], row[3]
            csvWriter.writerow(line)
        else:
            cnt_found +=1
            print 'found!'
#         line = row[0], row[1], row[2]
#         print name, line 
#         print row
#         print row[1].decode('gbk')
    print total, cnt_found, 'missed ',cnt_missed                            
                        
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
if  __name__ == '__main__':
    if len(sys.argv)<2:
        print 'No action specified.'
        print '--1: txt2csv, list all words aligned.'
        print '--2: stock_daemon'
        print '--3: get_price_map'
        print '--4: get_price_map from .csv'
        sys.exit()
            
    if sys.argv[1].startswith('--'):
        option=sys.argv[1][2:]            
        # fetch sys.argv[1] but without the first two characters
        if option=='1':
            txt2csv1('word2.txt', 'gh.csv')
            txt2csv2('pdf2.txt', 'cctv.csv')
        elif option=='2':
            check_if_included('cctv_final.csv', 'gh_final.csv','missed.csv')    
        elif option=='3':
            beep_sos()

            
    print 'main done!'