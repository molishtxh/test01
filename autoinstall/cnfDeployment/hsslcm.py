#!/usr/bin/python3

import os
import sys
import re
import datetime
import time
from optparse import OptionParser
import logging
import subprocess

lcmOptions={\
"deploy":"                       Include download package, generate netconf/helm values/secret.tar/ss7 link, onboard image/charts, upload netconf/secret, SS7 Link/License to ZTS, deploy HSS CNF and health check ",\
"deploy_only":"                  Include upload netconf&secrets to ZTS, deploy HSS CNF and health check.",\
"prepare_all":"                  Include download package, generate netconf/helm values/secret.tar/upload ss7 link&license.",\
"prepare_all_without_download":" Include generate netconf/helm values/secret.tar/upload ss7 link&license.",\
"onboard_images_charts":"        Include onboarding images and helm charts.",\
"prepare_netconf":"              Auto generate netconf xml base on configure file.",\
"prepare_helm_values":"          Auto generate helm values base on configure file.",\
"prepare_ss7_link":"             Auto generate ss7 link with SIGP IP and LPC IP.",\
"health_check":"                 Check the HSS CNF health state.",\
"terminate":"                    Terminate HSS CNF.",\
"cleanup_image_charts":"         Clean the image and charts of HSS CNF."}

cnfCfgFileName = "cnfdeployment.cfg"
helmValuesCfgFileName = "valuesYamlTemplate.yaml"
configureMap = {}
logfile = ""
lcmMode = "deploy"
logger = logging.getLogger(__name__)
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

def usageMsg():
    msg = "Usage: /usr/bin/python3 hsslcm.py -m [LCMMODE] -i [ConfigureFileName] -y [HelmValuesInputFile]\n\n"\
          "Commands:\n"
    for key, value in lcmOptions.items():
        msg += "  " + key + value + "\n"
    msg += "\nFor example:\n"\
           "    /usr/bin/python3 hsslcm.py -m deploy -i cnfdeployment.cfg -y valuesYamlTemplate.yaml\n"\
           "    /usr/bin/python3 hsslcm.py -m prepare_all -i cnfdeployment.cfg -y valuesYamlTemplate.yaml\n"\
           "    /usr/bin/python3 hsslcm.py -m prepare_helm_values -i cnfdeployment.cfg -y valuesYamlTemplate.yaml\n"\
           "    /usr/bin/python3 hsslcm.py -m prepare_all_without_download -i cnfdeployment.cfg -y valuesYamlTemplate.yaml\n"\
           "    /usr/bin/python3 hsslcm.py -m deploy_only -i cnfdeployment.cfg\n"
    return msg

def logFile():
    global logfile
    global logger
    path = os.path.basename(__file__).split(".")[0]
    path = path + "_log"
    if not os.path.exists(path):
        os.mkdir(path)
    logfile = path + "/hsslcm-" + lcmMode + "-" + time.strftime('%Y%m%d-%H-%M', time.localtime(time.time())) + ".log"
    print("The log file is " + logfile)
    logger.setLevel(level=logging.DEBUG)
    time_line = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    handler = logging.FileHandler(logfile, mode='w')
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(console)

def cmd_exec(cmd, msg):
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    pdu_data, stderr_pdu = proc.communicate(
        ('through stdin to stdout').encode())
    data = pdu_data.decode()
    err = stderr_pdu.decode()
    resultcode = proc.returncode
    if resultcode != 0:
        logger.error(msg + (data).strip() + (err).strip())
        sys.exit(-1)
    logger.info((data).strip())

def deploy():
    logger.info("============deploy start===========")
    prepare_all()
    onboard_images_charts()
    deploy_only()

def deploy_only():
    logger.info("============deploy_only start========")
    upload_netconf_secret_files()
    upload_ss7_link_license()
    create_networkpolicy()
    labInstall()

def prepare_all():
    logger.info("============prepare all start========")
    download_package("enable")
    prepare_netconf()
    prepare_helm_values()
    generate_secret_tar()
    generate_ss7_link()

def prepare_all_without_download():
    logger.info("============prepare all without download start========")
    download_package("disable")
    prepare_netconf()
    prepare_helm_values()
    generate_secret_tar()
    generate_ss7_link()

def download_package(enable):
    cmd = "./download_package.sh " + pkgPath + " " + loadNum + " " + enable
    msg = "download package & unTar package failed with error: "
    cmd_exec(cmd, msg)

def health_check():
    logger.info("============health check========")
    cmd = pythonPath + " health_check.py " + vnfname + " " + hssNameSpace + " " + controlIP + " " + controlPwd + " " + controlUser
    msg = "health check failed with error: "
    cmd_exec(cmd, msg)

def prepare_helm_values():
    logger.info("============generate value.yaml========")
    configPath = pkgPath + loadNum + "/CONFIGURATION/"
    os.system("rm -rf " + configPath + "values.yaml")
    valuesYaml = "cms-8200-hss-nt-hlr_values.yaml"
    cmd = "cp " + configPath + valuesYaml + " " + configPath + "values.yaml; " + pythonPath + " getValues.py helm_values_fileName=" + helmValuesCfgFileName + " zts1user_passwd=" + zts1UserPasswd + " zts_namespace=" + ztsNameSpace + " vnf_name=" + vnfname + " use_resource=" + useResource + " value_path=" + configPath + "values.yaml" + " storage_class=" + storageClass + " tenant_enabled=" + tenantEnabled + " tenant_name=" + tenantName
    msg = "values.yaml generation failed with error: "
    cmd_exec(cmd, msg)

def prepare_netconf():
    logger.info("============generate netconf.xml========")
    configPath = pkgPath + loadNum + "/CONFIGURATION/"
    miscPath = pkgPath + loadNum + "/INSTALL_MEDIA/MISC/"
    ndsGenericFile = "cms-8200-hss-nt-hlr_nds_generic.xml"
    os.system("rm -rf " + configPath + vnfname + ".xml" )
    os.system("cp " + configPath + ndsGenericFile + " " + configPath + vnfname + ".xml")
    os.system("cp ./generateCNXML.sh " + miscPath)
    cmd = miscPath + "/generateCNXML.sh " + configPath + vnfname + " HSS_HLR_Client_IpAddress1=" + pgwDSIP + " HSS_HLR_Client_IpAddress2=" + pgwIP + " HSS_LDAP_Host=" + LDAPHost + " HLR_LDAP_Host=" + LDAPHost + " HLR_FE_Logical_Node=" + HLRdFELogicalNode + " HLR_LN_Address=" + LNAddress + " HLR_PointCode_From_Helm=" + pointCodeFromHelm + " HSS_Server_IpAddress="+ pgwDSIP + "; ./updateGenericConf.sh " + configPath + vnfname + ".xml"
    msg = "netconfig xml generation failed with error: "
    cmd_exec(cmd, msg)

def generate_secret_tar():
    logger.info("============generate secret-provision.tar========")
    miscPath = pkgPath + "/" + loadNum + "/INSTALL_MEDIA/MISC/"
    if not os.path.exists(miscPath + "smProvisionData"):
        os.system("cd " + miscPath + "; tar xvf smProvisionData.tar.gz")
    cmd = "cd " + miscPath + "smProvisionData/; " + pythonPath + " secretsCli.py prepareDefault --vnfid " + vnfname
    msg = "secret generation failed with error: "
    cmd_exec(cmd, msg)

def upload_netconf_secret_files():
    logger.info("============Upload netconf xml and secret-provision.tar========")
    caclientfile = scriptHome + "caclientcli"
    if not os.path.exists(caclientfile):
        os.system("curl http://artifactory-blr1.ext.net.nokia.com/artifactory/ims-meta-local/mcc_imscontainer_tools/22.2/caclientcli -o " + caclientfile)
    cmd = pythonPath + " uploadFiles.py -v " + vnfname + " -p " + zts1UserPasswd + " -z " + ztsEnvoylbIP +  " -c " + caclientfile + " -n " + pkgPath + loadNum + "/CONFIGURATION/" + vnfname + ".xml" + " -s " + pkgPath + loadNum + "/INSTALL_MEDIA/MISC/smProvisionData/secret-provision.tar"
    logger.info(cmd)
    msg = "upload netconf&secret failed with error: "
    cmd_exec(cmd, msg)

def checkInput(parser, options):
    if not options.lcmMode or not options.fileName:
        parser.error("incorrect number of arguments")
        sys.exit(2)
    if options.lcmMode not in lcmOptions.keys():
        parser.error("option mode is invalid")
        sys.exit(2)
    if options.lcmMode in ['deploy', 'prepare_all', 'prepare_helm_values', 'prepare_all_without_download']  and not options.NfileName:
        parser.error("No argument -y/--file1 for values yaml generation.")
        sys.exit(2)
    if options.fileName and (not os.path.exists(options.fileName)):
        print(str(options.fileName) + " file1 is not exist.")
        sys.exit(-1)
    if options.NfileName and (not os.path.exists(options.NfileName)):
        print(str(options.NfileName) + " file1 is not exist.")
        sys.exit(-1)

def generate_ss7_link():
    logger.info("============genereate_ss7_link========")
    cmd = pythonPath + " licenseFileStore.py generate "+cnfCfgFileName
    msg = "Link generate failed with error: "
    cmd_exec(cmd, msg)

def upload_ss7_link_license():
    logger.info("============upload_ss7_link_license========")
    cmd = pythonPath + " licenseFileStore.py upload " + cnfCfgFileName
    msg = "Link/License upload failed with error: "
    cmd_exec(cmd, msg)

def labInstall():
    logger.info("============labInstall========")
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "bringUpHssCnf.sh", scriptDest)
    bringUpHssCnf = scriptDest + "/bringUpHssCnf.sh "+cnfCfgFileName
    cmd = loginContainerCmd + "\"" + bringUpHssCnf + "\""
    msg = "labInstall failed with error: "
    cmd_exec(cmd, msg)

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
    cmd_exec(cmd, msg)

def cleanup_image_charts():
    logger.info("============cleanup_image_charts========")
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "deleteCnf.sh", scriptDest)
    imageclean = scriptDest + "/deleteCnf.sh imageclean "+cnfCfgFileName
    cmd = loginContainerCmd  + "\""+imageclean+"\"" 
    msg = "CleanupImg failed with error: "
    cmd_exec(cmd, msg)

    helmclean = scriptDest + "/deleteCnf.sh helmclean "+cnfCfgFileName
    cmd = loginContainerCmd  + "\""+helmclean+"\"" 
    msg = "CleanupHelm failed with error: "
    cmd_exec(cmd, msg)

def delete_cm():
    cmd = pythonPath + " deleteCM.py "+cnfCfgFileName
    msg = "deleteCM failed with error: "
    cmd_exec(cmd, msg)

def delete_secrets():
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    cpDir(scriptHome + "deleteCnf.sh", scriptDest)
    cmd = scriptDest +"/deleteCnf.sh cadel "+cnfCfgFileName
    msg = "deleteSecrts failed with error: "
    cmd_exec(cmd, msg)

def create_bcmt_container():
    cmd = scriptHome + "createBcmtContainer.sh "+cnfCfgFileName
    msg = "Failed to create create bcmt-admin container with error: "
    cmd_exec(cmd, msg)

def cpDir(srcDir, destDir):
    if not os.path.exists(srcDir):
        print ("%s does not exist" % srcDir)
        sys.exit(-1)
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    cmd = "cp -r " + srcDir + " " + destDir
    msg = ("Failed to cp files from %s to %s with error:" % (srcDir, destDir))
    cmd_exec(cmd, msg)

def create_tenant_or_ns():
    create_bcmt_container()
    scriptDest = "/opt/bcmt/" + vnfname + "/script/"
    os.system("rm -rf " + scriptDest)
    cpDir(scriptHome + "createTenantOrNS.sh", scriptDest)
    cpDir(scriptHome + cnfCfgFileName, scriptDest)
    createFile = scriptDest + "createTenantOrNS.sh"
    cmd = loginContainerCmd + createFile
    msg = "Failed to create tenant or namespace with error: "
    cmd_exec(cmd, msg)

def create_networkpolicy():
    scriptDest = "/opt/bcmt/" + vnfname + "/script"
    cpDir(scriptHome, scriptDest)
    scriptFile = scriptDest + "/createNetPolicy.sh "+cnfCfgFileName
    cmd = loginContainerCmd +'\"' + scriptFile + '\"'
    msg = "Failed to create networkpolicy: "
    cmd_exec(cmd, msg)

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


if "__main__" == __name__:
    parser = OptionParser(usageMsg())
    parser.add_option("-m", "--mode", dest="lcmMode", help="HSS CNF deployment options.")
    parser.add_option("-i", "--file", dest="fileName", help="read data from FILENAME")
    parser.add_option("-y", "--file1", dest="NfileName", help="read network data from FILENAME")
    (options, args) = parser.parse_args()
    checkInput(parser, options)
    lcmMode = options.lcmMode
    cnfCfgFileName = options.fileName
    helmValuesCfgFileName = options.NfileName

    logFile()
    parseCnfCfg()

    pkgPath = configureMap['NREG_PKG_PATH']
    hssNameSpace = configureMap['HSS_NAMESPACE']
    vnfname = configureMap['VNFID']
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
    # In NCS22, podman replaces docker
    containerCommand = subprocess.check_output('which podman &>/dev/null && echo podman || echo docker', shell = True).decode().strip()
    loginContainerCmd = containerCommand + " exec -i bcmt-admin-" + vnfname + " bash -c "
    if lcmMode == 'deploy':
        deploy()
    elif lcmMode == 'deploy_only':
        deploy_only()
    elif lcmMode == "prepare_all":
        prepare_all()
    elif lcmMode == "prepare_all_without_download":
        prepare_all_without_download()
    elif lcmMode == "prepare_netconf":
        prepare_netconf()
    elif lcmMode == "prepare_helm_values":
        prepare_helm_values()
    elif lcmMode == "prepare_ss7_link":
        generate_ss7_link()
    elif lcmMode == "health_check":
        health_check()
    elif lcmMode == "terminate":
        terminate()
    elif lcmMode == "cleanup_image_charts":
        cleanup_image_charts()
    elif lcmMode == "onboard_images_charts":
        onboard_images_charts()
