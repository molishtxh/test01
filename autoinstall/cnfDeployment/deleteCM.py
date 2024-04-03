#!/usr/bin/python
import os
import pexpect
import sys
import re
import getpass
import paramiko
import datetime
import collections
import yaml
import ipaddress

cnfCfgFileName = sys.argv[1]
configureMap = {}


def parseCnfCfg():
    file = open(cnfCfgFileName, 'r')
    lines = file.read().split('\n')
    lines = [x for x in lines if len(x) > 0]
    lines = [x for x in lines if x[0] != '#']
    lines = [x for x in lines if x[0] != '[']
    lines = [x.rstrip().lstrip() for x in lines]
    for line in lines:
        configureMap[line.split('=')[0]] = (line.split('=')[1]).strip("'")
    print(configureMap)


def getCaSecret():
    global casecret
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(zts_ctrl_ip, username=zts_user, password=zts_passwd)
    stdout = client.exec_command('kubectl get secrets -n '+ vnf_namespace +' | grep -i '+vnf_name+'casecret')[1]
    casecret = len(stdout.readlines())
    print(casecret)
    
 



def deleteVNF():
    global zts_ctrl_ip
    print(zts_ctrl_ip)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(zts_ctrl_ip, username=zts_user, password=zts_passwd)
    stdout = client.exec_command('kubectl get pods -o wide -n'+ zts_namespace +' |grep -i cmcontrol|awk \'{print $1}\'')[1]
    cmcontrol_pod = (stdout.readlines()[0]).strip()
    print(cmcontrol_pod)
    child = pexpect.spawnu("ssh " + zts_user + "@" + zts_ctrl_ip)
    fout = open ("/tmp/lcmvnflog.txt", "w")
    child.logfile = fout
    ret = child.expect([pexpect.TIMEOUT,'Are you sure you want to continue connecting','[p|P]assword:'])
    if ret == 0:
        print('[-] Error Connecting')
        return
    if ret == 1:
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT,'[p|P]assword'])
        if ret == 0:
            print('[-] Error Connecting')
            return
    child.sendline(zts_passwd)
    getctrlInfoCmd = 'kubectl exec -it ' + cmcontrol_pod + ' -n '+ zts_namespace  +' -- cmcli getctrlinfo '
    child.sendline(getctrlInfoCmd)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'Please Enter UserName:'])
    if ret != 2:
        print("No expected enter cm username")
        return
    child.sendline(cm_user)
    child.expect('Please Enter Password:')
    child.sendline(cm_passwd)
    child.expect([pexpect.EOF,pexpect.TIMEOUT])
    file_obj = open("/tmp/lcmvnflog.txt")
    print(vnf_name)
    global cmserver
    cmserver = ""
    for line in file_obj:
        if vnf_name in line and "cmserver" in line:
            line = re.sub( '\s+', ' ', line ).strip()
            cmserver = line.split(' ')[1]
            file_obj.close
            break
    if cmserver == "":
        print("vnf name with " + vnf_name + " is not exist, skip delete vnf.")
        return
    print('kubectl exec -it ' + cmserver + ' -n '+ zts_namespace +' -- cmcli DeleteVNF ' + vnf_name)
    child.sendline('kubectl exec -it ' + cmserver +' -n '+ zts_namespace  + ' -- cmcli DeleteVNF ' + vnf_name)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)There is no UNDO for this action, Are you sure to proceed with Delete(?i)'])
    if ret != 2:
        print("No expected 'Are you sure to proceed with Delete'")
        return
    child.sendline('y')
    child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)Please Enter UserName:(?i)'])
    child.sendline(cm_user)
    child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)Please Enter Password:(?i)'])
    child.sendline(cm_passwd + '\n')
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)Successfully(?i)'],timeout=200)
    if ret != 2:
        print("DeleteVNF " + vnf_name + " failed, please check.")
    else:
        print("DeleteVNF " + vnf_name + " done.")
    child.close()

def deleteEsymac():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(zts_ctrl_ip, username=zts_user, password=zts_passwd)
    stdout = client.exec_command('kubectl get pods -o wide -n '+ zts_namespace +' |grep -i integration-internal|awk \'{print $1}\'')[1]
    integration_pod = (stdout.readlines()[0]).strip()
    print(integration_pod)
    child = pexpect.spawnu("ssh " + zts_user + "@" + zts_ctrl_ip)
    fout = open ("/tmp/lcmvnflog.txt", "w")
    child.logfile = fout
    ret = child.expect([pexpect.TIMEOUT,'Are you sure you want to continue connecting','[p|P]assword:'])
    if ret == 0:
        print('[-] Error Connecting')
        return
    if ret == 1:
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT,'[p|P]assword'])
        if ret == 0:
            print('[-] Error Connecting')
            return
    child.sendline(zts_passwd)
    #getctrlInfoCmd = 'kubectl exec -it ' + integration_pod + " -- bash -c ' cd /opt/SettingsCli && ./settingscli  -list Destination'"
    getctrlInfoCmd = 'kubectl exec -it ' + integration_pod + ' -n '+ zts_namespace  +" -- bash -c ' cd /opt/SettingsCli && ./settingscli -delete VNFSettings -i '" + vnf_name
    print(getctrlInfoCmd)
    child.sendline(getctrlInfoCmd)

    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'Enter Username:'])
    if ret != 2:
        print("No expected enter um username")
        return
    child.sendline(um_user)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'Enter Password:'])
    child.sendline(um_passwd)
    child.expect([pexpect.EOF,pexpect.TIMEOUT])
    child.close()


def getInput():
    global vnf_name
    global zts_ctrl_ip
    global zts_user
    global zts_passwd
    global zts_namespace
    global cm_user
    global cm_passwd
    global vnf_namespace
    global casecret

    vnf_name=configureMap['VNFID']
    print(vnf_name)

    zts_ctrl_ip=configureMap['CONTROL_IP']
    print(zts_ctrl_ip)

    zts_user=configureMap['CONTROL_USER']
    print(zts_user)

    zts_passwd=configureMap['CONTROL_PWD']
    print(zts_passwd)

    zts_namespace=configureMap['ZTS_NAMESPACE']
    print(zts_namespace)

    cm_user=configureMap['CM_USER']
    print(cm_user)

    cm_passwd=configureMap['CM_USER_PWD']
    print(cm_passwd)

    vnf_namespace=configureMap['HSS_NAMESPACE']
    print(vnf_namespace)
   


parseCnfCfg()
getInput()
getCaSecret()

if(casecret == 0):
  print("delete cmserver")
  deleteVNF()
  #deleteEsymac()
else:
  print("casecret exist, please delete cmserver by yourself")
