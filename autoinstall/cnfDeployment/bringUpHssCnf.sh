#!/bin/bash

#set -x

scriptHome=$(cd "$(dirname "$0")";pwd)
echo $scriptHome
source $scriptHome/${1}

helmInstall(){
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD
    
    mkdir -p $INSTALL_FOLDER'/tmp'
    INSTALL_FOLDER=$INSTALL_FOLDER'/tmp'
    
    # Get the certification content
    cd $INSTALL_FOLDER
    ncs kubectl get secret harbor-harbor-nginx-srt -n ncms -o yaml | grep -e ca.crt | awk -F ":" '{print $2}' > tmpca.crt
    sed -i '$d' tmpca.crt
    str=$(cat tmpca.crt)
    echo $str |base64 -d >ca.crt
    echo "ca.crt file is generated under folder $INSTALL_FOLDER"
    cd $INSTALL_FOLDER; rm -rf tmpca.crt

    harbor_url=https://$CONTROL_IP:30003/chartrepo/$TENANT_NAME/
    echo "harbor_url is $harbor_url"
    ncs helm3 repo --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD add harbor-$TENANT_NAME $harbor_url --ca-file $INSTALL_FOLDER/ca.crt

    ncs helm3 repo update

    
    OLD_IFS=$IFS
    IFS=","
    arr=($CHART_LIST)
    IFS="$OLD_IFS"
    for chart in ${arr[@]}
    do
    if [[ ${chart} =~ 'cluster' ]];then
       ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD
    else 
       ncs user login --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD
    fi
    #nreg-hss-hlr-cluster  nreg-hss-hlr-cluster-security  nreg-hss-hlr-network  dco  hssxds  etcd  nreg-hss-hlr
    if [[ $chart == 'nreg-hss-hlr' ]];
    then 
       ncs helm3 install $VNFID harbor-$TENANT_NAME/nreg-hss-hlr --version $CHART_VERSION -f $VALUE_PATH --timeout 30m --namespace $HSS_NAMESPACE --ca-file $INSTALL_FOLDER/ca.crt  --wait
    else
       charttype=$(echo -e $chart | sed -r 's/nreg-hss-hlr-//g')
       ncs helm3 install $VNFID-$charttype harbor-$TENANT_NAME/$chart --version $CHART_VERSION -f $VALUE_PATH --timeout 5m --namespace $HSS_NAMESPACE --ca-file $INSTALL_FOLDER/ca.crt --wait
    fi

    result=$?
    if [[ ${result} -eq 0 ]]; then
        echo " Successfully execute helm install $chart command."
    else
        echo "Failed to execute helm install $chart command."
        exit 1
    fi
    done

    sleep 1m
}



helmInstallNoTenant(){
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    #ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD
    
    OLD_IFS=$IFS
    IFS=","
    arr=($CHART_LIST)
    IFS="$OLD_IFS"
    for chart in ${arr[@]}
    do
    #nreg-hss-hlr-cluster  nreg-hss-hlr-cluster-security  nreg-hss-hlr-network  dco  hssxds  etcd  nreg-hss-hlr
    if [[ $chart == 'nreg-hss-hlr' ]];
    then 
       ncs helm3 install $VNFID stable/nreg-hss-hlr --version $CHART_VERSION -f $VALUE_PATH --timeout 15m --namespace $HSS_NAMESPACE --wait
    else
       charttype=$(echo -e $chart | sed -r 's/nreg-hss-hlr-//g')
       ncs helm3 install $VNFID-$charttype stable/$chart --version $CHART_VERSION -f $VALUE_PATH --timeout 5m --namespace $HSS_NAMESPACE --wait
    fi

    result=$?
    if [[ ${result} -eq 0 ]]; then
        echo " Successfully execute helm install $chart command."
    else
        echo "Failed to execute helm install $chart command."
        exit 1
    fi
    done

    sleep 1m
}


helmInstallOperator(){
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD

    mkdir -p $INSTALL_FOLDER'/tmp'
    INSTALL_FOLDER=$INSTALL_FOLDER'/tmp'

    # Get the certification content
    cd $INSTALL_FOLDER
    ncs kubectl get secret harbor-harbor-nginx-srt -n ncms -o yaml | grep -e ca.crt | awk -F ":" '{print $2}' > tmpca.crt
    sed -i '$d' tmpca.crt
    str=$(cat tmpca.crt)
    echo $str |base64 -d >ca.crt
    sed -i 's/^/  /' ca.crt
    echo "ca.crt file is generated under folder $INSTALL_FOLDER"
    cd $INSTALL_FOLDER; rm -rf tmpca.crt

    harbor_url=https://$CONTROL_IP:30003/chartrepo/$TENANT_NAME/
    echo "harbor_url is $harbor_url"
    ncs helm3 repo --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD add harbor-$TENANT_NAME $harbor_url --ca-file $INSTALL_FOLDER/ca.crt

    ncs helm3 repo update


    echo "operator started"

    repostr=$(cat ca.crt)
    ( cat <<eof
url: $harbor_url
user: $TENANT_ADMIN_USR
password: $TENANT_ADMIN_PWD
caFile: |-
$repostr
eof
) >helmrepo_values.yaml

    existCRD=$(ncs kubectl get crd | grep profiles )
    if [[  $existCRD == "" ]]; then
       crdCreate=""
    else
       crdCreate=",crd.create=false"
    fi
 
    ncs helm3 install app-api harbor-$TENANT_NAME/ncm-app --namespace $HSS_NAMESPACE --set helm3Only=true,controller=true,autonomous.enabled=true,namespaced.enabled=true,namespaced.allowCRDs=false,global.registry=harborharbor-core.ncms.svc/$TENANT_NAME/csf-dockerdelivered.repo.lab.pl.alcatel-lucent.com,global.servicetype=NREGLCM,global.vnftype=NREG,global.vnfctype=LCM,global.vnfname=$VNFID,global.metadata_max_release=$major_release_version,global.metadata_min_release=$minor_release_version$crdCreate
    sleep 3m 

    ncs helm3 install nreg-hss-hlr-cluster harbor-$TENANT_NAME/nreg-hss-hlr-cluster -n $HSS_NAMESPACE -f $VALUE_PATH

    ncs helm3 install nreg-hss-hlr-cluster-security harbor-$TENANT_NAME/nreg-hss-hlr-clustersecurity -n $HSS_NAMESPACE -f $VALUE_PATH

    ncs user login --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD
    ncs helm3 install operator-repo harbor-$TENANT_NAME/helmrepo -n $HSS_NAMESPACE -f helmrepo_values.yaml
    ncs helm3 install $VNFID harbor-$TENANT_NAME/nreg-hss-hlr-profile -n $HSS_NAMESPACE --set tags="combined" -f $VALUE_PATH
    

    sleep 1m
}

helmInstallOperatorNoTenant(){
    echo "not supported"
}


main(){


    HSS_NUM_SIMPLE=`echo ${LOAD_NUM}|awk -F'-' '{print $2}'`  #2220055
    relNum1=`echo ${HSS_NUM_SIMPLE:0:2}`  #22
    relNum2=`echo ${HSS_NUM_SIMPLE:2:1}`   #2
    relNum=${relNum1}"."${relNum2}     #22.2
    loadNum=`echo ${HSS_NUM_SIMPLE:3:4}`
    loadNum=$(echo -e $loadNum | sed -r 's/0*([0-9])/\1/')  #55

    
    TENANT_ADMIN_USR=$TENANT_NAME'-admin'
    INSTALL_FOLDER='/opt/bcmt/'$VNFID
    CHART_VERSION="${relNum}.${loadNum}"
    VALUE_PATH=$INSTALL_FOLDER'/'$LOAD_NUM'/CONFIGURATION/values.yaml'
    major_release_version=$relNum1
    minor_release_version=$relNum2'.0'

    if [[ $TENANT_ENABLED == 'true' ]];
    then 
       HSS_NAMESPACE=$TENANT_NAME'-admin-ns'
    fi

    
    echo ${TENANT_ADMIN_USR}
    echo ${INSTALL_FOLDER}
    echo ${CHART_VERSION}

    if [[ $TENANT_ENABLED == 'true' ]] && [[ $IS_OPERATOR == 'true' ]]; then
       helmInstallOperator
    elif [[ $TENANT_ENABLED == 'true' ]] && [[ $IS_OPERATOR == 'false' ]]; then
       helmInstall
    elif [[ $TENANT_ENABLED == 'false' ]] && [[ $IS_OPERATOR == 'true' ]]; then
       helmInstallOperatorNoTenant
    else
       helmInstallNoTenant
    fi
    
    
}

main


