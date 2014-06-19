# -*- coding: utf-8 -*
import os, sys, time
import string
import urllib, urllib2
from selenium import webdriver
import re
import csv

webd_allone = None

def webdrv_init():
    #global webd_allone
    #if webd_allone == None:
    #    webd_allone = webdriver.Firefox()
    return 'webd_allonerv init\n'        
        
def webdrv_exit():        
    global webd_allone
    if webd_allone != None:
        webd_allone.quit()
    return 'webd_allonerv exit\n'        
        
def webdrv_get():
    global webd_allone
    if webd_allone == None:
        webd_allone = webd_alloneriver.Firefox()
    return webd_allone