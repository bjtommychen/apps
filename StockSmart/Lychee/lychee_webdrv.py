# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import re
import csv


#
#  ps aux | grep 'firefox/firefox' | awk '{print $2}' | xargs sudo kill -9
# 

webd_allone = None

def webdrv_init():
    #global webd_allone
    #if webd_allone == None:
    #    webd_allone = webdriver.Firefox()
    return 'webd_allonerv init\n'        
        
def webdrv_exit():        
    global webd_allone
    if webd_allone != None:
        webd_allone.close()
    return 'webd_allonerv exit\n'        
        
def webdrv_get():
    global webd_allone
    if webd_allone == None:
        webd_allone = webd_alloneriver.Firefox()
    return webd_allone