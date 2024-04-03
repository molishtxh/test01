#!/usr/bin/env python3
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
import configparser

cnfCfgFileName = sys.argv[2]
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

def getInput():
    global controlIP
    global controlUser
    global controlPwd
    global ztsNameSpace
    global cnf_namespace
    global dsadmin_passwd
    global vnf_name
    global license
    global LPC
    global key_path
    global install_path
    global load
    global sigpip
    
    controlIP=configureMap['CONTROL_IP']
    print(controlIP)
    
    controlUser=configureMap['CONTROL_USER']
    print(controlUser)

    controlPwd=configureMap['CONTROL_PWD']
    print(controlPwd)

    ztsNameSpace=configureMap['ZTS_NAMESPACE']
    print(ztsNameSpace)

    tenant_enable=configureMap['TENANT_ENABLED']
    tenant_name=configureMap['TENANT_NAME']
    cnf_namespace=configureMap['HSS_NAMESPACE']
    if tenant_enable == 'true':
       cnf_namespace=tenant_name+"-admin-ns"
    print(cnf_namespace)
    
    dsadmin_passwd=configureMap['DSADMIN_PWD']
    print(dsadmin_passwd)

    vnf_name=configureMap['VNFID']
    print(vnf_name)

    license=configureMap['KEY_LICENSE_PATH']
    print(license)

    LPC=configureMap['LPC']
    print(LPC)

    install_path='/opt/bcmt/'+vnf_name
    load=configureMap['LOAD_NUM']
    print(install_path)
    print(load)

    key_path=license[:license.rfind("/")]+ "/"

    pkgPath = configureMap['NREG_PKG_PATH']
    loadNum = configureMap['LOAD_NUM']
    imageSrcPath = pkgPath + loadNum
    VALUE_PATH=imageSrcPath+'/CONFIGURATION/values.yaml'
    sigpipTmp = os.popen("grep -ri -m1 sigplan: "+VALUE_PATH).readlines()[0]
    sigpip = sigpipTmp[sigpipTmp.find(":")+1:sigpipTmp.find("/")].strip()
    

def prePareLink():

    os.system("sshpass -p " + controlPwd + " scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null LinksDbToCli.sh " + controlUser + "@" + controlIP + ":"+ key_path)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(controlIP, username=controlUser, password=controlPwd)
    
    #stdout = client.exec_command('kubectl get pods -n '+ cnf_namespace +' |grep -i ss7|awk \'{print $1}\'')[1]
    #ss7pod = (stdout.readlines()[0]).strip()
    #print(ss7pod)
    #stdout = client.exec_command('kubectl describe pod '+ss7pod+' -n '+cnf_namespace+' | grep \"sigpLanhlr\" -A2 | tail -n 1 | sed \'s/\"//g\' | awk \'$1=$1\'')[1]
    #sigpip = (stdout.readlines()[0]).strip()
    #print(sigpip)
    stdout = client.exec_command("sed -i 's/SIGPIP/"+sigpip+"/g' "+key_path+"LinksDbToCli.sh;sed -i 's/LPCIP/"+LPC+"/g' "+key_path+"LinksDbToCli.sh")[1]
    
    
    

def fileUpload():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(controlIP, username=controlUser, password=controlPwd)
    stdout = client.exec_command('kubectl get pods -o wide -n '+ ztsNameSpace +' |grep -i envoylbf|awk \'{print $6}\'')[1]
    lbfip = (stdout.readlines()[0]).strip()
    print(lbfip)
   
    ##login control##
    child = pexpect.spawnu("ssh " + controlUser + "@" + controlIP)
    fout = open ("/tmp/licenseFileStoreLog.txt", "w")
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
    child.sendline(controlPwd)

    #login envoy#
    loginLBF = 'cd '+ key_path +';chmod 777 -R *; sftp -oPort=8099 dsadmin@'+ lbfip
    child.sendline(loginLBF)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'dsadmin@'+lbfip+'\'s password:'])
    if ret != 2:
        print("fileUpload No expected enter dsadmin")
        return
    child.sendline(dsadmin_passwd)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)Connected to (?i)'],timeout=10)
    if ret != 2:
        print("fileUpload envoy login failed, please check.")
        return

    #put LinksDbToCli#
    putLink = 'put LinksDbToCli.sh'
    child.sendline(putLink)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)100% (?i)'],timeout=5)
    if ret != 2:
        print("put LinksDbToCli failed, please check.")
        return
    print("put LinksDbToCli done.")
    
    #put licenseFile#
    putLicense = 'put M7-KEY-'+vnf_name+'.tar.gz'
    child.sendline(putLicense)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)100% (?i)'],timeout=5)
    if ret != 2:
        print("put licenseFile failed, please check.")
        return
    print("put licenseFile done.")
    
    bye = 'bye'
    child.sendline(bye)
    child.close()
    
def fileToEnvoy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(controlIP, username=controlUser, password=controlPwd)
    stdout = client.exec_command('kubectl get pods -o wide -n '+ ztsNameSpace +' |grep -i envoylbf|awk \'{print $6}\'')[1]
    lbfip = (stdout.readlines()[0]).strip()
    print(lbfip)
   
    ##login control##
    child = pexpect.spawnu("ssh " + controlUser + "@" + controlIP)
    fout = open ("/tmp/licenseFileStoreLog.txt", "w")
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
    child.sendline(controlPwd)

    
    #login envoy#
    loginLBF = 'ssh dsadmin@'+ lbfip + ' -p 8099'
    child.sendline(loginLBF)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'dsadmin@'+lbfip+'\'s password:'])
    if ret != 2:
        print("fileToEnvoy No expected enter dsadmin")
        return
    child.sendline(dsadmin_passwd)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)dsadmin(?i)'],timeout=10) 
    #if ret != 2: Authentication succeeded
        #print("fileToEnvoy envoy login failed, please check.")
        #return
    
    #dscli LinksDbToCli#
    putLink = 'dscli add file LinksDbToCli.sh -n sig -v '+vnf_name+" -r 1.0"
    child.sendline(putLink)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)100(?i)'],timeout=7)
    if ret != 2:
        ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)exists(?i)'],timeout=7)
        if ret == 2:
            putLink = 'dscli update file LinksDbToCli.sh -n sig -v '+vnf_name+" -r 1.0"
            child.sendline(putLink)
            ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)100(?i)'],timeout=7)
            if ret != 2:
                print("LinksDbToCli update failed, please check.")
                return
            else:
                print("LinksDbToCli update succeeded.")
        else:
            print("LinksDbToCli add failed, please check.")
            return
    else:
        print("LinksDbToCli add succeeded.")


    #dscli licenseFile#
    licensefile='M7-KEY-'+vnf_name+'.tar.gz'
    putLicense = 'dscli add file '+ licensefile +' -n sig -v '+vnf_name+" -r 1.0"
    child.sendline(putLicense)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)100(?i)'],timeout=7)
    if ret != 2:
        ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)exists(?i)'],timeout=7)
        if ret == 2:
            putLicense = 'dscli update file '+ licensefile +' -n sig -v '+vnf_name+" -r 1.0"
            child.sendline(putLicense)
            ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'(?i)100(?i)'],timeout=7)
            if ret != 2:
                print("licenseFile update failed, please check.")
                return
            else:
                print("licenseFile update succeeded.")
        else:
            print("licenseFile add failed, please check.")
            return
    else:
        print("licenseFile add succeeded.")
      
    child.close()

parseCnfCfg()
getInput()
if sys.argv[1] == "generate": 
    prePareLink()
if sys.argv[1] == "upload":
    fileUpload()
    fileToEnvoy()


