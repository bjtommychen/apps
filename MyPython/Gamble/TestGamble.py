import time
import sys
import os
import socket
import math
import csv
import random 
from pandas import DataFrame, Series
import pandas as pd
import matplotlib.pyplot as plt
 
 
def test_random():
    total = 1000
    cnt0 = 0
    cnt1 = 0
    check_val = 0
    check_cnt = 0
    val = 0
    cnt = 0
    for i in range(0, total):
        val = random.randrange(0,2,1)
        if val == 0:
            cnt0+=1
        elif val == 1:
            cnt1+=1
        if val == check_val:
            check_cnt += 1
        else:
            if check_cnt > cnt:
                cnt = check_cnt
                val = check_val
            check_cnt = 0
            check_val = val
    print 'cnt0', cnt0, 'cnt1', cnt1
    print 'check_cnt',  cnt, 'check_val', val
    time.sleep(1)
 
#return True if I lose. 
def check_win():
    val = random.randrange(0,2,1)
    if val == 0:
        return False
    elif val == 1:
        return True

def test_gamble():
    fund = 10000
    idx = 1
    last_skip = False
    log = []
    while fund > 0:
        print 'No. ', idx, 50*'*'
        bet = 10
        if last_skip:
            bet *= 10
        change = 0
        fund_start = fund
        last_skip = False
        round = 1
        while fund:
            print 'bet', bet
            if bet > fund/4:# or round > 5:
                print 'SKIP THIS !', bet
                last_skip = True
                #time.sleep(2)
                break
            if fund < 1000 or fund > 50000:
                fund = 0
                break
            if bet > fund:
                print 'RUN OUT OF FUND!'
                print 'Round result:', fund
                exit(0)
            if check_win(): #if they win this round
                change = (-bet)
                if round < 4:
                    bet *= 3    
                elif round < 6:
                    bet *= 2.2
                else:
                    bet *= 2
                #print 'lose, change', change,
                fund += change
                #print 'fund left', fund                
            else:
                change = (bet)
                #print 'win, change', change ,
                fund += change
                #print 'fund left', fund                
                break
            round += 1

        print 'Round result:', fund, ', Round change:', fund-fund_start
        if abs(fund-fund_start) > 500:
            time.sleep(.1)
        log.append(fund)
        idx += 1
        #time.sleep(round/10)
    # Plot
    data = Series(log)
    data.plot()
    plt.show()
 
if  __name__ == '__main__':
    test_random()
    test_gamble()
    print 'done.'
    exit()