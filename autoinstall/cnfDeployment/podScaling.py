#!/usr/bin/python3
import subprocess
import os
import sys
import time
import yaml

'''
podScaling(podType, cnfCfgFileName)
1. podType: dlb
2. cnfCfgFileName: /root/abc/cnfdeployment.cfg
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
    file.close()

def getInput():
    global controlNodeIP
    global controlNodeUSER
    global controlNodePWD
    global namespace_name
    global cnfName
    global loadNumber

    controlNodeIP = configureMap['CONTROL_IP']
    print("NCS control node IP: " + controlNodeIP)
    controlNodeUSER = configureMap['CONTROL_USER']
    print(controlNodeUSER)
    controlNodePWD = configureMap['CONTROL_PWD']
    print(controlNodePWD)
    namespace_name = configureMap['HSS_NAMESPACE']
    print("CNF name space: " + namespace_name)
    cnfName = configureMap['VNFID']
    print("CNF name: " + cnfName)
    loadNumber = configureMap['LOAD_NUM']
    print("Load number: " + loadNumber)

# NREG_22.2-2220141  ===> nreg-hss-hlr-22.2.141.tgz, then upload to control node /tmp
def upload_chart_version():
    print("lOAD_NUM: " + loadNumber)
    bcmtDir="/opt/bcmt/"+cnfName+"/"+loadNumber+"/INSTALL_MEDIA/CHARTS/"

    iloadNumber = str.split(loadNumber, "-")
    chart_pkg = "nreg-hss-hlr-" + iloadNumber[1][0:2] + "." + iloadNumber[1][2:3] + "." + iloadNumber[1][
                                                                                              4:7] + ".tgz"
    print("chart path: "+chart_pkg)

    os.system("sshpass -p " + controlNodePWD + \
              " scp -r -q "+bcmtDir+chart_pkg +" "+ controlNodeUSER + \
              "@" + controlNodeIP + ":/tmp/"+chart_pkg)
    return chart_pkg

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

def backup_values_yaml():
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " helm3 get values " + cnfName + " -n " + namespace_name + \
                  " \\> /tmp/tmp_values.yaml"
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    output, err = pp.communicate()
    print("values.yaml has been saved as /tmp/tmp_values.yaml")

def prepare_scalin_yaml():
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " helm3 get values " + cnfName + " -n " + namespace_name
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    output, err = pp.communicate()
    m_yaml = yaml.load(output.decode().strip(), yaml.SafeLoader)
    print("updated existing values.yaml: ")
    print(m_yaml)

    replicaCount = int(m_yaml[podType]['replicaCount'])
    if replicaCount <= 1:
        print("only 1 pod, not possible to scaling in further!")
        sys.exit(1)
    replicaCount -= 1
    m_yaml[podType]['replicaCount'] = replicaCount
    print("updated values.yaml: ")
    print(m_yaml)

    if os.path.exists("/tmp/tmp_scaling_in.yaml"):
        os.remove("/tmp/tmp_scaling_in.yaml")
    stream = open("/tmp/tmp_scaling_in.yaml", "w+")
    yaml.dump(m_yaml,
              stream,
              default_flow_style=False,
              encoding='utf-8',
              allow_unicode=True)
    stream.close()

    os.system("sshpass -p " + controlNodePWD + \
              " scp -r -q /tmp/tmp_scaling_in.yaml " + controlNodeUSER + \
              "@" + controlNodeIP + ":/tmp/tmp_scaling_in.yaml")

def clean_up():
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " rm /tmp/tmp_values.yaml"
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " rm /tmp/tmp_scaling_in.yaml"
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " rm " + chart_path
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)

########################################### Main ##################################
parseCnfCfg()
getInput()
os.system("sshpass -p " + controlNodePWD + \
          " scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null sshpass " + controlNodeUSER + \
          "@" + controlNodeIP + ":/usr/bin")
# check pod parameter before taking any further action
if podType not in ['dlb']:
    print("pod type is not supported")
    sys.exit(1)
# check pod status
if pod_health_check():
    print("pod is not healthy")
    sys.exit(1)
# scale out will use orig values.yaml
backup_values_yaml()

# Trig scale in.
# example:helm3 upgrade qdlab1 -f ./values_scalein.yaml ./nreg-hss-hlr-22.2.104.tgz --namespace=hss-admin-ns --no-hooks
prepare_scalin_yaml()

chart_path = "/tmp/"+upload_chart_version()

podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
              + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + " -f /tmp/tmp_scaling_in.yaml " \
              + chart_path + " --namespace=" + namespace_name + " --no-hooks"
print(podName_cmd)

pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
output, err = pp.communicate()

# wait pod scaling in completed
counter = 1
time.sleep(20)
while counter <= 40:
    print("Wait 10s for pod scaling:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
    time.sleep(10)
    if pod_health_check() == 0:
        print("pod get back to health")
        break
    counter += 1
if counter >40:
    print("pod scaling takes too long!!!")
    clean_up()
    sys.exit(1)
print("pod scale in completed")

# Step into pod scale out (back)
podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
              + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + " -f /tmp/tmp_values.yaml " \
              + chart_path + " --namespace=" + namespace_name + " --no-hooks"
print(podName_cmd)
pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
output, err = pp.communicate()

# wait pod scaling in completed
counter = 1
time.sleep(20)
while counter <= 40:
    print("Wait 10s for pod scaling:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
    time.sleep(10)
    if pod_health_check() == 0:
        print("pod get back to health")
        break
    counter += 1
if counter >40:
    print("pod scaling takes too long!!!")
    clean_up()
    sys.exit(1)
print("pod scale out completed")

clean_up()
################### return ###############################################
sys.exit(0)

