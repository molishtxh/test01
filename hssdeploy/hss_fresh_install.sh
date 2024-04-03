#!/bin/bash

NAME_SPACE="hssfire"
VNFID="qdlab1"
APS_DIR=$(cd `dirname $0`; pwd)
source ${APS_DIR}/get_APS_Rel.sh
VALUES_YAML="${APS_DIR}/values_${Rel_1}.${Rel_2}.yaml"
#zts_envoy_ip="10.67.32.113"
zts_envoy_ip="10.67.35.15"

##FTSDL2##
#FEDS="10.255.8.158"
#PGW="10.255.8.87"
#PGWDS="10.255.8.163"
##PT-OneNDS1##
#FEDS="10.67.26.20"
#PGW="10.67.26.10"
#PGWDS="10.67.26.9"
##OneNDS_Int##
#FEDS="10.9.229.36"
#PGW="10.9.229.38"
#PGWDS="10.9.229.39"
##PTSDL1##
FEDS="10.255.8.34"
PGW="10.255.8.215"
PGWDS="10.255.8.47"
##PTSDL2##
#FEDS="10.255.28.15"
#PGW="10.255.28.143"
#PGWDS="10.255.28.34"

set -x
##### ======= update_xml begin =======
if [[ ! -f ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml.bak ]];then
cp ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml.bak
fi
sed -i 's/##HSS_Server_IpAddress##/'${PGW}'/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HSS_HLR_Client_IpAddress2##/'${PGW}'/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HSS_LDAP_Host##/'${FEDS}'/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HSS_HLR_Client_IpAddress1##/'${PGWDS}'/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HLR_FE_Logical_Node##/1/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HLR_LN_Address##/49170440/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HLR_PointCode_From_Helm##/1001/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
sed -i 's/##HLR_LDAP_Host##/'${FEDS}'/g' ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
cd ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/MISC;tar -zxvf smProvisionData.tar.gz
cd ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/MISC/smProvisionData/;python3 secretsCli.py prepareDefault --vnfid ${VNFID}
python3 ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/MISC/uploadFiles.py -v ${VNFID} -p User@1234 -z ${zts_envoy_ip} -c ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/MISC/caclientcli -n ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml -s ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/MISC/smProvisionData/secret-provision.tar
if [[ $? -ne 0 ]];then
echo "executing uploadFiles.py failed, exit..."
exit 1
fi
##### ======= update_xml end =======
sleep 5

##### ======= hss_install begin =======
APS_old=`grep IMSDL ${VALUES_YAML} |head -1|awk '{printf $2}'|cut -c 6-`
if [ ${APS} -ne ${APS_old} ];then
sed -i 's/'${APS_old}'/'${APS}'/g' ${VALUES_YAML}
fi
date;helm3 install ${VNFID}-cluster ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-cluster-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-cluster-security ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-cluster-security-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-network ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-network-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-dco ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/dco-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-etcd ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/etcd-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-xds ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/hssxds-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-db ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/crdb-redisio-hss_${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID}-cnsba ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/cnsba-controller-hss_${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
date;helm3 install ${VNFID} ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} --timeout 15m;date
date;helm3 install ${VNFID}-debugassist ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/debugassist-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE};date
##### ======= hss_install end =======
