#!/usr/bin/python3
'''
1.download image, and onboard
	//script is ready by Jiangjiang/Catherine, by need enhancement.

2. get the values.yaml and then migrate to the new version.
helm3 get values qdlab1 -n hss-admin-ns > values.yaml
	2.1: get orig values. //script is ready
	2.2: migrate: from Binson/Paul by Jan 21

3.helm3 upgrade the 7 charts in order.
	helm3 upgrade qdlab1-network -f ./433/values_pt.yaml ./433/nreg-hss-hlr-network-22.0.433.tgz --namespace=pthss
	helm3 upgrade qdlab1-cluster -f ./433/values_pt.yaml ./433/nreg-hss-hlr-cluster-22.0.433.tgz  --namespace=pthss
	helm3 upgrade qdlab1-cluster-security  -f ./433/values_pt.yaml ./433/nreg-hss-hlr-cluster-security-22.0.433.tgz --namespace=pthss
	helm3 upgrade qdlab1-etcd -f ./433/values_pt.yaml ./433/etcd-22.0.433.tgz --namespace=pthss
	helm3 upgrade qdlab1-dco -f ./433/values_pt.yaml ./433/dco-22.0.433.tgz --namespace=pthss
	helm3 upgrade qdlab1-hssxds -f ./433/values_pt.yaml ./433/hssxds-22.0.433.tgz --namespace=pthss
	helm3 upgrade qdlab1 -f ./433/values_pt.yaml ./433/nreg-hss-hlr-22.0.433.tgz --namespace=pthss --timeout 20m
'''

import subprocess
import os
import sys
import time
# import yaml
# import cnf_values_migration as yaml_migrate
import hsslcm as pkg_handler
import rolling_back as rb

cnf_configure_file = sys.argv[1]
configureMap = {}


def parse_cnf_cfg():
    with open(cnf_configure_file, 'r') as file:
        lines = file.read().split('\n')
        lines = [x for x in lines if len(x) > 0]
        lines = [x for x in lines if x[0] != '#']
        lines = [x for x in lines if x[0] != '[']
        lines = [x.rstrip().lstrip() for x in lines]
        for line in lines:
            configureMap[line.split('=')[0]] = (line.split('=')[1]).strip("'")
        print(configureMap)
        file.close()


def get_input():
    global controlNodeIP
    global controlNodeUSER
    global controlNodePWD
    global namespace_name
    global cnfName
    global fromLoadNumber
    global targetLoadNumber
    global pkgPath

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
    fromLoadNumber = configureMap['LOAD_NUM']
    print("From Load number: " + fromLoadNumber)
    targetLoadNumber = configureMap['NEXT_LOAD_NUM']
    print("Target Load number: " + targetLoadNumber)
    pkgPath = configureMap['NREG_PKG_PATH']
    print("Package path: " + pkgPath)
    operatorMode = configureMap['IS_OPERATOR']
    print("Operator mode: " + operatorMode)


# NREG_22.2-2220141  ===> nreg-hss-hlr-22.2.141.tgz, then upload to control node /tmp
def upload_chart_version():
    print("NEXT_lOAD_NUM: " + targetLoadNumber)
    chartsDir = pkgPath + targetLoadNumber + "/INSTALL_MEDIA/CHARTS/"

    cmd="sshpass -p " + controlNodePWD + \
        " scp -r -q " + chartsDir + " " + controlNodeUSER + \
        "@" + controlNodeIP + ":/tmp/"
    print(cmd)
    os.system(cmd)


def load_number_to_tag():
    print("lOAD_NUM: " + targetLoadNumber)
    iloadNumber = str.split(targetLoadNumber, "-")
    _tag = iloadNumber[1][0:2] + "." + iloadNumber[1][2:3] + "." + iloadNumber[1][4:7]
    print("tag is: " + _tag)
    return _tag


def pod_health_check(pod_type):
    podName_cmd = "sshpass -p " + controlNodePWD + \
                  " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + controlNodeUSER + \
                  "@" + controlNodeIP + " kubectl get pods " + " -n " + namespace_name + "| grep " + cnfName + \
                  "-" + pod_type + "| awk '{print $2}'"
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


def backup_values_yaml(yaml_path):
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " helm3 get values " + cnfName + " -n " + namespace_name
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    output, err = pp.communicate()
    with open(yaml_path, "w", encoding="utf-8") as orig_yaml_file:
        orig_yaml_file.truncate()
        orig_yaml_file.write(output.decode().strip())
        orig_yaml_file.close()
        del orig_yaml_file


# to be refacted
def _clean_up():
    """
    backup_yaml_path = "/tmp/" + cnfName + "_tmp_backup_values.yaml"
    target_yaml_path = "/tmp/" + cnfName + "_tmp_target_values.yaml"
    _yaml_path = "/tmp/CHARTS/*"
    """
    print("local clean up")
    _cmd = "rm -rf /tmp/" + cnfName +" *.yaml"
    os.system(_cmd)

    print("remote clean up")
    podName_cmd = "sshpass -p " + controlNodePWD + " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " rm -rf /tmp/CHARTS/"+cnfName+"/*"
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)




if "__main__" == __name__:
    parse_cnf_cfg()
    get_input()
    # In NCS22, podman replaces docker
    containerCommand = subprocess.check_output('which podman &>/dev/null && echo podman || echo docker', shell = True).decode().strip()
    loginContainerCmd = containerCommand + " exec -it bcmt-admin-" + cnfName + " bash -c "

    # download image
    cmd = "./download_package.sh " + pkgPath + " " + targetLoadNumber + " enable"
    os.system(cmd)

    # onboard image
    #cp images/charts to /opt/bcmt/vnfname dir
    imageDestPath = "/opt/bcmt/" + cnfName
    imageSrcPath = pkgPath + targetLoadNumber
    os.system("rm -rf " + imageDestPath)
    pkg_handler.cpDir(imageSrcPath, imageDestPath)

    scriptHome = "."
    if os.path.dirname(sys.argv[0]) != "":
        scriptHome = os.path.dirname(sys.argv[0]) + "/"
    scriptHome = scriptHome + "/"
    scriptDest = "/opt/bcmt/" + cnfName + "/script/"
    pkg_handler.cpDir(scriptHome + cnf_configure_file, scriptDest)
    pkg_handler.cpDir(scriptHome + "onboardingScript.sh", scriptDest)
    onboardFile = scriptDest + "onboardingScript.sh " + cnf_configure_file +" "+targetLoadNumber
    print(onboardFile)
    print(loginContainerCmd)
    loginCmd = loginContainerCmd + '\"' + onboardFile + '\"'
    print(loginCmd)
    os.system(loginCmd)

    # prepare value.yaml
    backup_yaml_path = "/tmp/" + cnfName + "_tmp_backup_values.yaml"
    target_yaml_path = "/tmp/" + cnfName + "_tmp_target_values.yaml"
    template_yaml_path = "/elk/demo/auto/" + targetLoadNumber + "/CONFIGURATION/cms-8200-hss-nt-hlr_values.yaml"
    backup_values_yaml(backup_yaml_path)
    tmp_num = str.split(targetLoadNumber, "-")
    to_load = tmp_num[1][0:2] + "." + tmp_num[1][2:3]
    tmp_num = str.split(fromLoadNumber, "-")
    from_load = tmp_num[1][0:2] + "." + tmp_num[1][2:3]
    # ./cnf_values_migration.py -s 22.0 -t 22.2 -f from_load_value.yaml -m template yaml -o output yaml file
    cmd = "python3 cnf_values_migration.py -s 22.0 -t " + to_load + " -f " + backup_yaml_path + \
          " -m " + template_yaml_path + " -o " + target_yaml_path
    print(cmd)
    os.system(cmd)
    # upload CHARTs and yaml to control node
    upload_chart_version()
    cmd="sshpass -p " + controlNodePWD + " scp -r -q " + target_yaml_path + " " + controlNodeUSER + \
        "@" + controlNodeIP + ":/tmp/CHARTS/."
    print(cmd)
    os.system(cmd)
    _yaml_path = "/tmp/CHARTS/" + cnfName + "_tmp_target_values.yaml"
    # trig upgrade and expire timer let's take it as 1 hour
    _tag_ = load_number_to_tag()

    if operatorMode.lower() != 'true':
      # step 1: upgrade network
      podName_cmd = "sshpass -p " + controlNodePWD + \
                    " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                    + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + "-network -f " \
                    + _yaml_path + " /tmp/CHARTS/nreg-hss-hlr-network-" + _tag_ + \
                    ".tgz --namespace=" + namespace_name
      print(podName_cmd)
      pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
      time.sleep(10)

    # step 2: upgrade cluster
    podName_cmd = "sshpass -p " + controlNodePWD + \
                  " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + "-cluster -f " \
                  + _yaml_path + " /tmp/CHARTS/nreg-hss-hlr-cluster-" + _tag_ + \
                  ".tgz --namespace=" + namespace_name
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         shell=True)
    time.sleep(10)
    # Step 3: upgrade cluster security
    podName_cmd = "sshpass -p " + controlNodePWD + \
                  " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                  + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + "-cluster-security -f " \
                  + _yaml_path + " /tmp/CHARTS/nreg-hss-hlr-cluster-security-" + _tag_ + \
                  ".tgz --namespace=" + namespace_name
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         shell=True)
    time.sleep(10)

    if operatorMode.lower() != 'true':
      # step 4: upgrade etcd
      podName_cmd = "sshpass -p " + controlNodePWD + \
                    " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                    + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + "-etcd -f " \
                    + _yaml_path + " /tmp/CHARTS/etcd-" + _tag_ + \
                    ".tgz --namespace=" + namespace_name
      print(podName_cmd)
      pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         shell=True)
      counter = 1

      time.sleep(20)
      while counter <= 40:
          print("Wait 10s for etcd upgrade:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
          time.sleep(10)
          if pod_health_check("etcd") == 0:
              print("pod get back to health")
              break
          counter += 1
      if counter > 40:
          print("etcd upgrade failure, trig roll back")
          rb.cnf_roll_back(controlNodeIP, controlNodeUSER, controlNodePWD, cnfName, namespace_name)
          _clean_up()
          sys.exit(1)

      # step 5: upgrade dco
      podName_cmd = "sshpass -p " + controlNodePWD + \
                    " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                    + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + "-dco -f " \
                    + _yaml_path + " /tmp/CHARTS/dco-" + _tag_ + \
                    ".tgz --namespace=" + namespace_name
      print(podName_cmd)
      pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         shell=True)
      counter = 1

      time.sleep(20)
      while counter <= 40:
          print("Wait 10s for dco upgrade:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
          time.sleep(10)
          if pod_health_check("dco") == 0:
              print("pod get back to health")
              break
          counter += 1
      if counter > 40:
          print("dco upgrade failure, trig roll back")
          rb.cnf_roll_back(controlNodeIP, controlNodeUSER, controlNodePWD, cnfName, namespace_name)
          _clean_up()
          sys.exit(1)

      # step 6: upgrade hssxds
      podName_cmd = "sshpass -p " + controlNodePWD + \
                    " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                    + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + "-hssxds -f " \
                    + _yaml_path + " /tmp/CHARTS/hssxds-" + _tag_ + \
                    ".tgz --namespace=" + namespace_name
      print(podName_cmd)

      pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
      counter = 1
      time.sleep(20)
      while counter <= 40:
          print("Wait 10s for hssxds upgrade:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
          time.sleep(10)
          if pod_health_check("hssxds") == 0:
              print("pod get back to health")
              break
          counter += 1
      if counter > 40:
          print("XDS upgrade failure, trig roll back")
          rb.cnf_roll_back(controlNodeIP, controlNodeUSER, controlNodePWD, cnfName, namespace_name)
          _clean_up()
          sys.exit(1)

    # step 7: callp upgrade
    if operatorMode.lower() != 'true':
      podName_cmd = "sshpass -p " + controlNodePWD + \
                    " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                    + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + " -f " \
                    + _yaml_path + " /tmp/CHARTS/nreg-hss-hlr-" + _tag_ + \
                    ".tgz --namespace=" + namespace_name
    else:
      podName_cmd = "sshpass -p " + controlNodePWD + \
                    " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " \
                    + controlNodeUSER + "@" + controlNodeIP + " helm3 upgrade " + cnfName + " -f " \
                    + _yaml_path + " /tmp/CHARTS/nreg-hss-hlr-profile" + _tag_ + \
                    ".tgz --namespace=" + namespace_name + \
                    "--set tags=\"combined\""

    print(podName_cmd)

    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    counter = 1
    time.sleep(20)
    while counter <= 40:
        print("Wait 10s for dlb, callp upgrade:" + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
        time.sleep(10)
        if pod_health_check("dlb") == 0:
            print("pod get back to health")
            break
        counter += 1
    if counter > 40:
        print("dlb upgrade failure, trig roll back")
        rb.cnf_roll_back(controlNodeIP, controlNodeUSER, controlNodePWD, cnfName, namespace_name)
        _clean_up()
        sys.exit(1)
    # if upgrade failed, trig rollback
    # rb.cnf_roll_back(controlNodeIP, controlNodeUSER, controlNodePWD, cnfName, namespace_name)

    # clean up env (yaml files, charts, what ever created, uploaded to control node
    _clean_up()

    # bye
    sys.exit(0)
