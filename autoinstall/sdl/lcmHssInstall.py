#!/usr/bin/python3

import os
import sys
import re
import datetime
import time
from optparse import OptionParser
import logging
import subprocess
import common

#specfic product
import lcmCommon

cnfCfgFileName = "cnfdeployment.cfg"
helmValuesCfgFileName = "valuesYamlTemplate.yaml"
configureMap = {}
scriptHome = os.path.dirname(sys.argv[0])
pythonPath = "/usr/bin/python3 "

scriptHome = "."
if os.path.dirname(sys.argv[0]) != "":
    scriptHome = os.path.dirname(sys.argv[0]) + "/"
scriptHome = scriptHome + "/"

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

def deploy():
    lcmCommon.logger.info("============deploy start===========")
    prepare_all()
    deploy_only()

def deploy_only():
    lcmCommon.logger.info("============deploy_only start========")
    upload_netconf_secret_files()
    upload_ss7_link_license()
    create_networkpolicy()
    labInstall()

def prepare_all():
    lcmCommon.logger.info("============prepare all start========")
    download_package()
    prepare_netconf()
    prepare_helm_values()
    generate_secret_tar()
    generate_ss7_link()
    onboard_images_charts()

def download_package():
    cmd = "./download_package.sh " + pkgPath + " " + loadNum
    msg = "download package & unTar package failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def health_check():
    lcmCommon.logger.info("============health check========")
    cmd = pythonPath + " health_check.py " + vnfname + " " + hssNameSpace + " " + controlIP + " " + controlPwd + " " + controlUser
    msg = "health check failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def prepare_helm_values():
    lcmCommon.logger.info("============generate value.yaml========")
    configPath = pkgPath + loadNum + "/CONFIGURATION/"
    os.system("rm -rf " + configPath + "values.yaml")
    valuesYaml = "cms-8200-hss-nt-hlr_values.yaml"
    cmd = "cp " + configPath + valuesYaml + " " + configPath + "values.yaml; " + pythonPath + " getValues.py helm_values_fileName=" + helmValuesCfgFileName + " zts1user_passwd=" + zts1UserPasswd + " zts_namespace=" + ztsNameSpace + " vnf_name=" + vnfname + " use_resource=" + useResource + " value_path=" + configPath + "values.yaml" + " storage_class=" + storageClass + " tenant_enabled=" + tenantEnabled + " tenant_name=" + tenantName
    msg = "values.yaml generation failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def prepare_netconf():
    lcmCommon.logger.info("============generate netconf.xml========")
    configPath = pkgPath + loadNum + "/CONFIGURATION/"
    miscPath = pkgPath + loadNum + "/INSTALL_MEDIA/MISC/"
    ndsGenericFile = "cms-8200-hss-nt-hlr_nds_generic.xml"
    os.system("rm -rf " + configPath + vnfname + ".xml" )
    os.system("cp " + configPath + ndsGenericFile + " " + configPath + vnfname + ".xml")
    os.system("cp ./generateCNXML.sh " + miscPath)
    cmd = miscPath + "/generateCNXML.sh " + configPath + vnfname + " HSS_HLR_Client_IpAddress1=" + pgwDSIP + " HSS_HLR_Client_IpAddress2=" + pgwIP + " HSS_LDAP_Host=" + LDAPHost + " HLR_LDAP_Host=" + LDAPHost + " HLR_FE_Logical_Node=" + HLRdFELogicalNode + " HLR_LN_Address=" + LNAddress + " HLR_PointCode_From_Helm=" + pointCodeFromHelm + " HSS_Server_IpAddress="+ pgwDSIP + "; ./updateGenericConf.sh " + configPath + vnfname + ".xml"
    msg = "netconfig xml generation failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def generate_secret_tar():
    lcmCommon.logger.info("============generate secret-provision.tar========")
    miscPath = pkgPath + "/" + loadNum + "/INSTALL_MEDIA/MISC/"
    if not os.path.exists(miscPath + "smProvisionData"):
        os.system("cd " + miscPath + "; tar xvf smProvisionData.tar.gz")
    cmd = "cd " + miscPath + "smProvisionData/; " + pythonPath + " secretsCli.py prepareDefault --vnfid " + vnfname
    msg = "secret generation failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def upload_netconf_secret_files():
    lcmCommon.logger.info("============Upload netconf xml and secret-provision.tar========")
    caclientfile = scriptHome + "caclientcli"
    if not os.path.exists(caclientfile):
        os.system("curl http://artifactory-blr1.ext.net.nokia.com/artifactory/ims-meta-local/mcc_imscontainer_tools/22.2/caclientcli -o " + caclientfile)
    cmd = pythonPath + " uploadFiles.py -v " + vnfname + " -p " + zts1UserPasswd + " -z " + ztsEnvoylbIP +  " -c " + caclientfile + " -n " + pkgPath + loadNum + "/CONFIGURATION/" + vnfname + ".xml" + " -s " + pkgPath + loadNum + "/INSTALL_MEDIA/MISC/smProvisionData/secret-provision.tar"
    lcmCommon.logger.info(cmd)
    msg = "upload netconf&secret failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def generate_ss7_link():
    lcmCommon.logger.info("============genereate_ss7_link========")
    cmd = pythonPath + " licenseFileStore.py generate "+cnfCfgFileName
    msg = "Link generate failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def upload_ss7_link_license():
    lcmCommon.logger.info("============upload_ss7_link_license========")
    cmd = pythonPath + " licenseFileStore.py upload " + cnfCfgFileName
    msg = "Link/License upload failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def labInstall():
    lcmCommon.logger.info("============labInstall========")
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "bringUpHssCnf.sh", scriptDest)
    bringUpHssCnf = scriptDest + "/bringUpHssCnf.sh "+cnfCfgFileName
    cmd = loginContainerCmd + "\"" + bringUpHssCnf + "\""
    msg = "labInstall failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def terminate():
    labUnInstall()
    delete_cm()

def labUnInstall():
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "deleteCnf.sh", scriptDest)
    deleteCnf = scriptDest + "/deleteCnf.sh uninstall "+cnfCfgFileName
    cmd = loginContainerCmd  + "\""+deleteCnf+"\"" 
    msg = "labUnInstall failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def cleanup_image_charts():
    lcmCommon.logger.info("============cleanup_image_charts========")
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "deleteCnf.sh", scriptDest)
    imageclean = scriptDest + "/deleteCnf.sh imageclean "+cnfCfgFileName
    cmd = loginContainerCmd  + "\""+imageclean+"\"" 
    msg = "CleanupImg failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

    helmclean = scriptDest + "/deleteCnf.sh helmclean "+cnfCfgFileName
    cmd = loginContainerCmd  + "\""+helmclean+"\"" 
    msg = "CleanupHelm failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def delete_cm():
    cmd = pythonPath + " deleteCM.py "+cnfCfgFileName
    msg = "deleteCM failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def delete_secrets():
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "deleteCnf.sh", scriptDest)
    cmd = scriptDest +"/deleteCnf.sh cadel "+cnfCfgFileName
    msg = "deleteSecrts failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def create_bcmt_container():
    cmd = scriptHome + "createBcmtContainer.sh "+cnfCfgFileName
    msg = "Failed to create create bcmt-admin container with error: "
    lcmCommon.cmd_exec(cmd, msg)

def cpDir(srcDir, destDir):
    if not os.path.exists(srcDir):
        print ("%s does not exist" % srcDir)
        sys.exit(-1)
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    cmd = "cp -r " + srcDir + " " + destDir
    msg = ("Failed to cp files from %s to %s with error:" % (srcDir, destDir))
    lcmCommon.cmd_exec(cmd, msg)

def create_tenant_or_ns():
    create_bcmt_container()
    scriptDest = "/opt/bcmt/" + vnfname + "/script/"
    os.system("rm -rf " + scriptDest)
    cpDir(scriptHome + "createTenantOrNS.sh", scriptDest)
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    createFile = scriptDest + "createTenantOrNS.sh"
    cmd = loginContainerCmd + createFile
    msg = "Failed to create tenant or namespace with error: "
    lcmCommon.cmd_exec(cmd, msg)

def create_networkpolicy():
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome, scriptDest)
    scriptFile = scriptDest + "/createNetPolicy.sh "+cnfCfgFileName
    cmd = loginContainerCmd +'\"' + scriptFile + '\"'
    msg = "Failed to create networkpolicy: "
    lcmCommon.cmd_exec(cmd, msg)

def onboard_images_charts():
    create_tenant_or_ns()

    # cp images/charts to /opt/bcmt/vnfname dir
    imageDestPath = "/opt/bcmt/" + vnfname
    imageSrcPath = pkgPath + loadNum
    os.system("rm -rf " + imageDestPath)
    cpDir(imageSrcPath, imageDestPath)

    # cp onboardingScript.sh to /opt/bcmt/vnfname dir
    scriptDest = "/opt/bcmt/" + vnfname + "/script/"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "onboardingScript.sh", scriptDest)
    onboardFile = scriptDest + "onboardingScript.sh "+cnfCfgFileName
    loginCmd = loginContainerCmd + '\"' + onboardFile + '\"'
    os.system(loginCmd)

class hssInstall(lcmCommon.installCnfProduct):
    def deployEntry(self):
        lcmCommon.logger.info("============deploy start===========")
        init()
        deploy()
    def preHealthcheckEntry(self):
        lcmCommon.logger.info("============to do===========")
    def prepareEntry(self):
        lcmCommon.logger.info("============prepare start===========")
        init()
        prepare_all()
    def deployOnlyEntry(self):
        lcmCommon.logger.info("============deploy only start===========")
        init()
        deploy_only()
    def postHealthcheckEntry(self):
        lcmCommon.logger.info("============post health check===========")
        init()
        health_check()
    def terminateEntry(self):
        lcmCommon.logger.info("============terminate start===========")
        init()
        terminate()

def init():
    global pkgPath
    global hssNameSpace
    global vnfname
    global pgwDSIP
    global pgwIP
    global LDAPHost
    global HLRdFELogicalNode
    global LNAddress
    global pointCodeFromHelm
    global zts1UserPasswd
    global ztsNameSpace
    global useResource
    global storageClass
    global loadNum
    global controlIP
    global controlUser
    global controlPwd
    global ztsEnvoylbIP
    global tenantEnabled
    global tenantName
    global loginContainerCmd

    parseCnfCfg()
#    pkgPath = configureMap['NREG_PKG_PATH']
    hssNameSpace = configureMap['HSS_NAMESPACE']
    vnfname = configureMap['VNFID']
    pkgPath = "/opt/bcmt/" + vnfname
    pgwDSIP = configureMap['PGWDS_IP']
    pgwIP = configureMap['PGW_IP']
    LDAPHost = configureMap['LDAP_HOST']
    HLRdFELogicalNode = configureMap['HLR_FE_Logical_Node']
    LNAddress = configureMap['HLR_LN_Address']
    pointCodeFromHelm = configureMap['PointCode_From_Helm']
    zts1UserPasswd = configureMap['ZTS1USER_PWD']
    ztsNameSpace = configureMap['ZTS_NAMESPACE']
    useResource = configureMap['USE_RESOURCE']
    storageClass = configureMap['STORAGE_CLASS']
    loadNum = configureMap['LOAD_NUM']
    controlIP = configureMap['CONTROL_IP']
    controlUser = configureMap['CONTROL_USER']
    controlPwd = configureMap['CONTROL_PWD']
    ztsEnvoylbIP = configureMap['ZTSENVOYLB_IP']
    tenantEnabled = configureMap['TENANT_ENABLED']
    tenantName = configureMap['TENANT_NAME']

    containerCommand = subprocess.check_output('which podman &>/dev/null && echo podman || echo docker', shell = True).decode().strip()
    loginContainerCmd = containerCommand + " exec -i bcmt-admin-" + vnfname + " bash -c "


