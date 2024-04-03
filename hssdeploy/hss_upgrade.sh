#!/bin/bash

NAME_SPACE="ptreg"
VNFID="qdlab1"
APS_DIR=$(cd `dirname $0`; pwd)
source ${APS_DIR}/get_APS_Rel.sh
VALUES_YAML="${APS_DIR}/values_${Rel_1}.${Rel_2}.yaml"

set -x
APS_in_yaml=$(grep IMSDL ${VALUES_YAML} |head -1|awk '{printf $2}'|cut -c 6-)
if [ ${APS} -ne ${APS_in_yaml} ];then
sed -i 's/'${APS_in_yaml}'/'${APS}'/g' ${VALUES_YAML}
fi

current_version=$(kubectl get deployments.apps -n ${NAME_SPACE} -o yaml |grep IMSDL|grep hsscallp|awk -F : '{print$4}'|cut -c 6-9)
upgraded_version=$(echo ${APS}|cut -c -4)
if [[ $current_version -lt $upgraded_version ]];then
hook_tag=""
elif [[ $current_version -eq $upgraded_version ]];then
hook_tag="--no-hooks"
else
echo "upgraded version is lower than current version, exit.."
exit 1
fi

date;helm3  upgrade ${VNFID}-cluster ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-cluster-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-cluster-security ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-cluster-security-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-network ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-network-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-dco ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/dco-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-etcd ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/etcd-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-xds ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/hssxds-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-db ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/crdb-redisio-hss_${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID}-cnsba ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/cnsba-controller-hss_${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
date;helm3  upgrade ${VNFID} ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/nreg-hss-hlr-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} --no-hooks --timeout 15m;date
date;helm3  upgrade ${VNFID}-debugassist ${APS_DIR}/NREG_${Rel_1}.${Rel_2}-${APS}/INSTALL_MEDIA/CHARTS/debugassist-${Rel_1}.${Rel_2_int}.${Rel_3_int}.tgz -f ${VALUES_YAML} -n ${NAME_SPACE} $hook_tag;date
