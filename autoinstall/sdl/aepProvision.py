#!/usr/bin/env python3
import os
import sys
import re
import getpass
import datetime
import time
from optparse import OptionParser
import logging
import subprocess
import common

def getInput():
    global testclient_ip 
    global testclient_user 
    global testclient_pwd 
    global aep_package_path_lpc 
    global exps_sequence 
    global pgwops_user
    global pgwops_pwd
    global pgwops
    global pgw_pwd
    global pgw
    
    configureMap = common.parseGlobalValues('./sdl_values.yaml')
    testclient_ip = configureMap['testclient_ip']
    testclient_user = configureMap['testclient_user']
    testclient_pwd = configureMap['testclient_pwd']
    aep_package_path_lpc = configureMap['aep_package_path_lpc']
    exps_sequence = configureMap['exps_sequence']
    pgwops_user =  configureMap['pgwops_user']
    pgwops_pwd = configureMap['pgwops_pwd']
    pgwops = configureMap['pgwops']
    pgw_pwd = configureMap['pgw_pwd']
    pgw = configureMap['pgw']
 

def aepProvision():

    copy_cmd = "sshpass -p " + testclient_pwd + " scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null provisionOperation.sh netconf-console " +testclient_user + "@" + testclient_ip + ":"+ aep_package_path_lpc

    exec_cmd = "sshpass -p "+ testclient_pwd+" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+testclient_user+ "@" + testclient_ip +" "+ aep_package_path_lpc+"/provisionOperation.sh "+aep_package_path_lpc+" "+exps_sequence+" "+pgwops_user+" "+pgwops_pwd+" "+ pgwops+ " "+pgw_pwd+" "+pgw

    pp = subprocess.Popen(copy_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    output, err = pp.communicate()

    pp = subprocess.Popen(exec_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    output, err = pp.communicate()
    
getInput()
aepProvision()



