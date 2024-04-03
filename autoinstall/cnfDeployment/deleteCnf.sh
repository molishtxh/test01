#!/bin/bash

set -x

scriptHome=$(cd "$(dirname "$0")";pwd)
echo $scriptHome
source $scriptHome/${2}


helmUnInstall(){
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD


    OLD_IFS=$IFS
    IFS=","
    arr=($CHART_LIST)
    IFS="$OLD_IFS"
    len=${#arr[@]}
    for((i=$len -1 ;i>=0; i--))
    do
    chart=${arr[$i]}
    #nreg-hss-hlr-cluster  nreg-hss-hlr-cluster-security  nreg-hss-hlr-network  dco  hssxds  etcd  nreg-hss-hlr
    if [[ $chart == 'nreg-hss-hlr' ]];
    then 
        ncs helm3 uninstall $VNFID -n $HSS_NAMESPACE --timeout 15m
        if [[ $? -eq 0 ]]; then
            count=`ncs helm3 list -a -n ${HSS_NAMESPACE}|grep ${VNFID}|grep -v "${VNFID}-"|wc -l`
            if [ ${count} -eq 0 ]; then
                echo " Successfully execute uninstall ${VNFID}."
            else
                ncs helm3 list -a -n ${HSS_NAMESPACE}|grep -v "${VNFID}-"
                echo "Failed to execute uninstall ${VNFID}."
                exit 1    
            fi
        else
            echo "Failed to execute uninstall ${VNFID}."
            exit 1
        fi
    else
        charttype=$(echo -e $chart | sed -r 's/nreg-hss-hlr-//g')
        ncs helm3 uninstall $VNFID-$charttype -n $HSS_NAMESPACE --timeout 15m
        if [[ $? -eq 0 ]]; then
            echo " Successfully execute uninstall ${VNFID}-${charttype}."
        else
            echo "Failed to execute uninstall ${VNFID}-${charttype}."
            exit 1    
        fi
    fi
    done

}


helmUnInstallOperator(){
    
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD


    #uninstall lab
    ncs helm3 uninstall $VNFID -n $HSS_NAMESPACE --timeout 15m
    if [[ $? -eq 0 ]]; then
        count=`ncs helm3 list -a -n ${HSS_NAMESPACE}|grep ${VNFID}|grep -v "${VNFID}-"|wc -l`
        if [ ${count} -eq 0 ]; then
            echo " Successfully execute uninstall ${VNFID}."
        else
            ncs helm3 list -a -n ${HSS_NAMESPACE}|grep -v "${VNFID}-"
            echo "Failed to execute uninstall ${VNFID}."
            exit 1
        fi
    else
        echo "Failed to execute uninstall ${VNFID}."
        exit 1
    fi


    #uninstall cluster
    ncs helm3 uninstall nreg-hss-hlr-cluster -n $HSS_NAMESPACE --timeout 15m
    if [[ $? -eq 0 ]]; then
        echo " Successfully execute uninstall ${VNFID}-cluster."
    else
        echo "Failed to execute uninstall ${VNFID}-cluster."
        exit 1
    fi


    #uninstall security
    ncs helm3 uninstall nreg-hss-hlr-security -n $HSS_NAMESPACE --timeout 15m
    if [[ $? -eq 0 ]]; then
        echo " Successfully execute uninstall ${VNFID}-security."
    else
        echo "Failed to execute uninstall ${VNFID}-security."
        exit 1
    fi

    #uninstall operator-repo
    ncs helm3 uninstall operator-repo -n $HSS_NAMESPACE --timeout 15m
    if [[ $? -eq 0 ]]; then
        echo " Successfully execute uninstall ${VNFID}-operator-repo."
    else
        echo "Failed to execute uninstall ${VNFID}-operator-repo."
        exit 1
    fi

    #uninstall app-api
    ncs helm3 uninstall app-api -n $HSS_NAMESPACE --timeout 15m
    if [[ $? -eq 0 ]]; then
        echo " Successfully execute uninstall ${VNFID}-app-api."
    else
        echo "Failed to execute uninstall ${VNFID}-app-api."
        exit 1
    fi
}


deleteCaSecret(){
    sshpass -p ${CONTROL_PWD} ssh  -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  ${CONTROL_USER}@${CONTROL_IP} "kubectl exec -it caserver-0 -n ${ZTS_NAMESPACE} -- /home/causer/del_user.sh ${VNFID}"
    sshpass -p ${CONTROL_PWD} ssh  -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  ${CONTROL_USER}@${CONTROL_IP} "kubectl get secrets -n ${HSS_NAMESPACE} | grep ${VNFID}"
    sshpass -p ${CONTROL_PWD} ssh  -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  ${CONTROL_USER}@${CONTROL_IP} "kubectl delete secrets -n ${HSS_NAMESPACE} ${VNFID}casecret"
    sshpass -p ${CONTROL_PWD} ssh  -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  ${CONTROL_USER}@${CONTROL_IP} "kubectl get secrets -n ${HSS_NAMESPACE} | grep ${VNFID}"
}



cleanUpImages(){

    # change to use hss admin user
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD

    echo "Starting to delete all images from harbor for tenant $TENANT_NAME:"
    imageList="
        $TENANT_NAME/corepaas-docker-local.bhisoj70.apac.nsn-net.net/ztsclustermonitoragent
        $TENANT_NAME/nokia/udm/lfsclient
        $TENANT_NAME/nokia/udm/udmenvoy
        $TENANT_NAME/nokia/hss/trigger
        $TENANT_NAME/nokia/hss/ss7stack
        $TENANT_NAME/nokia/hss/mcc
        $TENANT_NAME/nokia/hss/ldapdisp-mgnt
        $TENANT_NAME/nokia/hss/lcmhook
        $TENANT_NAME/nokia/udm/http2lb-mgmt
        $TENANT_NAME/nokia/udm/http2lb
        $TENANT_NAME/nokia/hss/hssxds
        $TENANT_NAME/nokia/hss/hssli
        $TENANT_NAME/nokia/hss/hssfla
        $TENANT_NAME/nokia/hss/hsscallp
        $TENANT_NAME/nokia/hss/testclient
        $TENANT_NAME/nokia/hss/hlrcallp
        $TENANT_NAME/nokia/hss/dlb
        $TENANT_NAME/nokia/udm/aws-ip-manager
        $TENANT_NAME/nokia/hss/arpf
        $TENANT_NAME/nokia/hss/admin
        $TENANT_NAME/nokia/hss/dco
        "
    echo "Images to be deleted:"
    echo "$imageList"
    
    for image in $imageList;
        do
        echo "Starting to delete images $image"
            ncs tenant-app-resource image delete --tenant_name $TENANT_NAME --image_name $image --tag_name $IMAGE_TAG 
            echo " images $image"
        done

    echo "Successfully delete images from harbor."
}

cleanUpHelmCharts(){

    # change to use hss admin user
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD
    
    chartList=$(ncs tenant-app-resource chart list --tenant_name $TENANT_NAME | grep name | awk -F ":" '{print $2}'| sed 's/\"//g' | sed 's/\,//g')
echo "$chartList"

    echo "Starting to delete charts for tenant $TENANT_NAME:"
    for chart in $chartList; do
        ncs tenant-app-resource chart delete --tenant_name $TENANT_NAME --chart_name $chart --chart_version $CHART_VERSION
    if [[ $? -eq 0 ]]; then
           echo "Successfully execute delete ${chart}, please wait..."
           sleep 5
    else
       echo "Failed to execute chart delete command."
    fi
    done

    echo "Successfully delete charts from harbor."
    
}

main(){

    HSS_NUM_SIMPLE=`echo ${LOAD_NUM}|awk -F'-' '{print $2}'`
    relNum1=`echo ${HSS_NUM_SIMPLE:0:2}`
    relNum2=`echo ${HSS_NUM_SIMPLE:2:1}`
    relNum=${relNum1}"."${relNum2}
    loadNum=`echo ${HSS_NUM_SIMPLE:3:4}`
    loadNum=$(echo -e $loadNum | sed -r 's/0*([0-9])/\1/')

    TENANT_ADMIN_USR=$TENANT_NAME'-admin'
    CHART_VERSION="${relNum}.${loadNum}"
    IMAGE_TAG="IMSDL"${HSS_NUM_SIMPLE}
    echo ${TENANT_ADMIN_USR}
    echo ${CHART_VERSION} 
    echo ${IMAGE_TAG}

    if [[ $TENANT_ENABLED == 'true' ]];
    then 
       HSS_NAMESPACE=$TENANT_NAME'-admin-ns'
    fi
    
    if [[ $operatorLab == 'uninstall' ]];
    then 
        if [[ $IS_OPERATOR == 'false' ]] ; then
           helmUnInstall
        else
           helmUnInstallOperator
        fi
    elif [[ $operatorLab == 'cadel' ]] ; then
        deleteCaSecret
    elif [[ $operatorLab == 'imageclean' ]] ; then
        cleanUpImages
    elif [[ $operatorLab == 'helmclean' ]] ; then
        cleanUpHelmCharts
    else
        echo "no action"
    fi
}

operatorLab=${1}

main



