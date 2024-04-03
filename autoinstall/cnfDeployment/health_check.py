#!/usr/bin/python3

import subprocess
import os
import sys
import datetime
import logging

helm_name = sys.argv[1]
namespace_name = sys.argv[2]
controlNodeIP= sys.argv[3]
controlNodePWD= sys.argv[4]
controlNodeUSER= sys.argv[5]

os.system("sshpass -p " + controlNodePWD + " scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null sshpass " + controlNodeUSER + "@" + controlNodeIP + ":/usr/bin")
###################To check postinstall pod status ##########
print("\n========================Checking postinstall status ========================\n")
postPod = "post"
podTypeName = helm_name + "-" + postPod
podName_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl get pods " + " -n " +  namespace_name + "| grep " +  podTypeName + "| grep Error | awk '{print $1}'"
pp = subprocess.Popen(podName_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
output, err = pp.communicate()
if output.decode().strip() != "":
    print("postinstall health check failed")
    sys.exit(1)
else:
    print("postinstall health check successful")
###################To check process status###################
print("\n========================Checking processes status ========================\n")
pTag = 0
podTypesforProcess = ["hsscallp", "dlb", "trigger", "arpf", "hssli", "hlrcallp", "ss7"]
for podType in podTypesforProcess:
    podTypeName = helm_name + "-" + podType
    podName_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl get pods " + " -n " +  namespace_name + "| grep " +  podTypeName + "| grep Running | awk '{print $1}'"
    p1 = subprocess.Popen(podName_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    output, err = p1.communicate()
    if output.decode().strip() == "":
       print(helm_name + "-" + podType + " is not health")
       exit(1)
    podNames = output.decode().strip().split("\n")
    for podName in podNames:
        print("checking pod: "  + podName)
        proc_status_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " \'kubectl exec -it " + podName + " -n " + namespace_name + ' -- /bin/bash -c "source /home/rtp99/.bash_profile;status1 -e"\''
        p = subprocess.Popen(proc_status_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        lines= output.decode().strip().split("\n")
        print(err)
        Tag = 0
        for line in lines:
            if "Processname" in line:
                Tag = 1
        #        pTag = 1
        if Tag == 1:
            for line in lines:
                if "=========" not in line and "Processname" not in line and "status1" not in line:
                    list = line.strip().split()
                    print("Process", list[0].strip(),"is unhealth and in",list[2],list[3],"state")
                    print("\n")
                    pTag = 1
                else:
                    print("line: " + line)
        if Tag == 0:
            print("Processes in the " + podName + " are health")
            print("\n")
if pTag == 1:
    print("==========   Processes are unhealth ===================\n") 
    sys.exit(1)
if pTag == 0:
    print("==========   All processes are health for each pod  ====================\n")

print("===============================checking  connection status ======================\n")

portTag = 0
for podType in podTypesforProcess:
    podTypeName = helm_name + "-" + podType
    podName_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl get pods " + " -n " +  namespace_name + "| grep " +  podTypeName + "| grep Running | awk '{print $1}'"
    p1 = subprocess.Popen(podName_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    output, err = p1.communicate()
    podNames = output.decode().strip().split("\n")
    for podName in podNames:
        onends_cmd = ""
        dia_cmd = ""
        trigger_cmd = ""
        ####oneNDS connectivity####
        if podType == "hsscallp" or podType == "hlrcallp":
            print("===============================checking OneNDS connectivity ======================\n")
            print("POD_NAME:" +  podName)
            onends_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl exec -it " + podName + " -n " + namespace_name + " -- netstat -na" + " |grep 1661 |grep -v CONNECTED | grep -v STREAM"
            p = subprocess.Popen(onends_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            output, err = p.communicate()
            if output.decode() != "" and "1661" and "ESTABLISHED" in output.decode():
                out=output.decode().strip().split("\n")
                for i in out:
                    print("OneNDS " + i.split()[4].split(":")[0] +" connection is ESTABLISHED to the port " + i.split()[4].split(":")[1] + " from ip " + i.split()[3].split(":")[0] + " and from port " + i.split()[3].split(":")[1])
            else:
                print(podName + ": OneNDS connection is not established : ",output,"\n")
                portTag = 1
        ####DIAMETER connectivity####
        elif podType == "dlb":
            print("\n=================Checking Diameter connectivity ====================================\n")
            print("POD_NAME:" +  podName)
            dia_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl exec -it " + podName + " -n " + namespace_name + " --  netstat -na" + "|grep -w 3868"
            p = subprocess.Popen(dia_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            outputdia, err = p.communicate()
            if outputdia.decode() != "" and "3868" and "LISTEN" in outputdia.decode():
                out=outputdia.decode().strip().split("\n")
                for i in out:
                    if "tcp" in i:
                        print("DIAMETER tcp connection is LISTENED to the port " + i.split()[3].split(":")[1] + " from ip " + i.split()[3].split(":")[0])
                    if "sctp" in i:
                        print("DIAMETER stcp connection is LISTENED to the port " + i.split()[1].split(":")[1] + " from ip " + i.split()[1].split(":")[0])
            else:
                print("DIAMETER connection is not established : ",outputdia.strip(),"\n")
                portTag = 1
        elif podType == "trigger":
            print("\n=================Checking Trigger connectivity ====================================\n")
            print("POD_NAME:" +  podName)
            trigger_rr_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl exec -it " + podName + " -n " + namespace_name + " -- netstat -na" + "|grep -w 50300"
            p = subprocess.Popen(trigger_rr_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            outputtriggerrr, err = p.communicate()
            if outputtriggerrr.decode() != "" and "50300" and "LISTEN" in outputtriggerrr.decode():
                out=outputtriggerrr.decode().strip().split("\n")
                for i in out:
                    print("Trigger RR connection is LISTENED to the port " + i.split()[3].split(":")[1] + " from ip " + i.split()[3].split(":")[0])
            else:
                print("Trigger  RR connection is not established : ",outputtriggerrr.strip(),"\n")
                portTag = 1
            trigger_bc_cmd = "sshpass -p " +  controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + "@" + controlNodeIP + " kubectl exec -it " + podName + " -n " + namespace_name + " --  netstat -na" + "|grep -w 50301"
            pbc = subprocess.Popen(trigger_bc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            outputtriggerbc, err = pbc.communicate()
            if outputtriggerbc.decode() != "" and "50301" and "LISTEN" in outputtriggerbc.decode():
                out=outputtriggerbc.decode().strip().split("\n")
                for i in out:
                    print("Trigger BC connection is LISTENED to the port " + i.split()[3].split(":")[1] + " from ip " + i.split()[3].split(":")[0])
            else:
                print("Trigger BC connection is not established : ",outputtriggerbc.strip(),"\n") 
                portTag = 1
if portTag == 1:
    print("==========  Port Connection are unhealth ===================\n")
    sys.exit(1)
if portTag == 0:
    print("==========   Port Connection  are health for each pod  ====================\n")
    sys.exit(0)
