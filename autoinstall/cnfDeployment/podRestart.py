#!/usr/bin/python3
import subprocess
import os
import sys
import time
'''
PodRestart(podType, cnfCfgFileName)
1. podType: dlb, dco
2. cnfCfgFileName: env avp
- return: 0-success, 1-failure
'''
podType = sys.argv[1]
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
    global controlNodeIP
    global controlNodeUSER
    global controlNodePWD
    global namespace_name
    global cnfName

    controlNodeIP=configureMap['CONTROL_IP']
    print("NCS control node IP: "+controlNodeIP)

    controlNodeUSER=configureMap['CONTROL_USER']
    print(controlNodeUSER)

    controlNodePWD=configureMap['CONTROL_PWD']
    print(controlNodePWD)

    namespace_name=configureMap['HSS_NAMESPACE']
    print("CNF name space: "+namespace_name)

    cnfName=configureMap['VNFID']
    print("CNF name: "+cnfName)

def pod_health_check():
    podName_cmd = "sshpass -p " + controlNodePWD + \
                  " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + \
                  "@" + controlNodeIP + " kubectl get pods " + " -n " + namespace_name + "| grep " + cnfName + \
                  "-" + podType + "| awk '{print $2}'"
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    output, err = pp.communicate()
    if output.decode().strip() == "":
        return 1
    else:
        mlist = output.decode().strip().split("\n")
        for pod in mlist:
            x = pod.split("/")
            if x[0] != x[1]:
                return 1
        return 0
parseCnfCfg()
getInput()
os.system("sshpass -p " + controlNodePWD + \
          " scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null sshpass " + controlNodeUSER + \
          "@" + controlNodeIP + ":/usr/bin")
###################To check pod parameter before taking any further action ##########
if podType not in ['dlb', 'dco']:
    print("pod type is not supported")
    sys.exit(1)

###################To check pod status###############################################
if pod_health_check():
    print("pod is not healthy")
    sys.exit(1)
###################To get pod id####################################################
podName_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
              + controlNodeUSER + "@" + controlNodeIP + " kubectl get pods " + " -n " +  namespace_name + "| grep " +  \
              podType + "| awk 'END{print $1}'"
pp = subprocess.Popen(podName_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
output, err = pp.communicate()
###################To delete pod####################################################
print("Restarting pod:" + output.decode().strip())
podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
              + controlNodeUSER + "@" + controlNodeIP + " kubectl delete pods " + output.decode().strip() + " -n " \
              + namespace_name
pp = subprocess.Popen(podName_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
output, err = pp.communicate()
###################To check pod status and timer is set to 30min####################################################
counter = 1
time.sleep(20)
while counter <= 40:
    print("Wait 10s for pod restarting:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
    time.sleep(10)
    if pod_health_check() == 0:
        print("pod get back to health")
        break
    counter += 1
if counter >40:
    print("pod restarting takes too long!!!")
    sys.exit(1)
print("pod restart finished")
sys.exit(0)
