#!/bin/bash
#example: sh scp_APS_from_bup.sh NREG_24.03-24030067
APS_DIR="/root/reed/deploy_upgrade"
source ${APS_DIR}/get_APS_Rel.sh
#set -x
echo "Start downloading..."
sshpass -p bup scp bup@10.67.30.14:/home/bup/CNF_IMAGE/${Rel_1}.${Rel_2}/IMSDL${APS}.000/NREG_${Rel_1}.${Rel_2}-${APS}.tar.gz .
if [[ $? -ne 0 ]];then
echo "NREG_${Rel_1}.${Rel_2}-${APS}.tar.gz doesn't exist...Latest version on bup is: "$(sshpass -p bup ssh bup@10.67.30.14 "ls -lrt /home/bup/CNF_IMAGE/${Rel_1}.${Rel_2}"|tail -10|awk '{printf $9" "}')
exit 1
fi
sleep 2
tar -zxvf NREG_${Rel_1}.${Rel_2}-${APS}.tar.gz;rm -rf NREG_${Rel_1}.${Rel_2}-${APS}.tar.gz
if [[ -f NREG_${Rel_1}.${Rel_2}-${APS}.tar ]];then
tar -zxvf NREG_${Rel_1}.${Rel_2}-${APS}.tar;rm -rf NREG_${Rel_1}.${Rel_2}-${APS}.tar
fi
ncs config set --endpoint=https://10.67.31.105:8084/ncm/api/v1
ncs user login --username=ncs-admin --password=Register#123
cd ${APS_DIR}/${1}/INSTALL_MEDIA/MISC; sh ncm_onboarding_script.sh local
