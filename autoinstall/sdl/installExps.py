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
    global control_ip 
    global control_user 
    global control_pwd 

    global sdl_namespace 
    global diag_pod_prefix 

    global sdl_citm_ext_oam
    global sdl_netconf_user
    global sdl_netconf_pwd

    global exps_to_be_installed_path
    global exps_sequence
    global operate_list
    
    configureMap = common.parseGlobalValues('./sdl_values.yaml')
    control_ip = configureMap['control_ip']
    control_user = configureMap['control_user']
    control_pwd = configureMap['control_pwd']

    sdl_namespace = configureMap['sdl_ns']
    diag_pod_prefix = configureMap['diag_pod_prefix']

    sdl_citm_ext_oam = configureMap['sdl_citm_ext_oam']
    sdl_netconf_user = configureMap['sdl_netconf_user']
    sdl_netconf_pwd = configureMap['sdl_netconf_pwd']

    exps_to_be_installed_path = configureMap['exps_to_be_installed_path']
    exps_sequence = configureMap['exps_sequence']
    operate_list = configureMap['operate_list']

def installExps():


    exec_cmd = "./installExps.sh " + control_ip + " " + control_user + " " + control_pwd + " " + sdl_namespace + " " + diag_pod_prefix + " " + sdl_citm_ext_oam  + " " + sdl_netconf_user + " " + sdl_netconf_pwd + " " + exps_to_be_installed_path + " " + exps_sequence + " " + operate_list

    pp = subprocess.Popen(exec_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    output, err = pp.communicate()
    
getInput()
installExps()



