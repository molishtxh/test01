#!/bin/bash

#set -x
sdlns=$1
pgwns=$2
sdlInstallPath=$3
pgwInstallPath=$4
sdlCrdPath=$5
pgwCrdPath=$6
product=$7

checkInstallResult(){
    if [[ $1 -eq 0 ]]; then
        echo " Successfully execute helm install $2 command."
    else
        echo "Failed to execute helm install $2 command."
        exit 1
    fi
}
sdlHelmNativeInstall(){	
	#sdloam install
	chartname="citm-ingress"
	podname="sdloam"
	helm3 install sdloam -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$chartname/values_extoam.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdlapp install
	chartname="citm-ingress"
	podname="sdlapp"
	helm3 install sdlapp   -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$chartname/values_extapp.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdldb install
	chartname="citm-ingress"
	podname="sdldb"
	helm3 install sdldb  -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$chartname/values_extdb.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-multus install
	chartname="multus"
	podname="sdl-multus"
	valuesyaml="infracommon/values.yaml"
	helm3 install sdl-multus -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-psp install
	chartname="psp"
	podname="sdl-psp"
	helm3 install sdl-psp -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-cmn install
	chartname="infracommon"
	podname="sdl-cmn"
	helm3 install sdl-cmn -n $sdlns $sdlInstallPath$chartname
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl1-kafka install
	chartname="ckaf-kafka"
	podname="sdl1-kafka"
	helm3 install sdl1-kafka -n $sdlns $sdlInstallPath$chartname --wait --timeout 1200s
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl1-kafka-ntf install
	chartname="ckaf-kafka-ntf"
	podname="sdl1-kafka-ntf"
	helm3 install sdl1-kafka-ntf -n $sdlns $sdlInstallPath$chartname --wait --timeout 1200s
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-access install
	chartname="dbaccess"
	podname="sdl-access"
	helm3 install sdl-access -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-storage install
	chartname="dbstorage"
	podname="sdl-storage"
	helm3 install sdl-storage -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-diag install
	chartname="diag"
	podname="sdl-diag"
	helm3 install sdl-diag -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-disco install
	chartname="disco"
	podname="sdl-disco"
	helm3 install sdl-disco -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-rtdblookup install
	chartname="rtdblookup"
	podname="sdl-rtdblookup"
	helm3 install sdl-rtdblookup -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-cas install
	chartname="cas"
	podname="sdl-cas"
	helm3 install sdl-cas -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-oes install
	chartname="oes"
	podname="sdl-oes"
	helm3 install sdl-oes -n $sdlns $sdlInstallPath$chartname -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#sdl-ntf install
	chartname="ntf"
	podname="sdl-ntf"
	helm3 install sdl-ntf -n $sdlns $sdlInstallPath$chartname --wait --timeout 3600s -f $sdlInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}

	sleep 1m
}

pgwHelmNativeInstall(){	
	#pgwinstance1 install
	chartname="citm-ingress"
	podname="pgwinstance1"
	helm3 install pgwinstance1 -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$chartname/values_instance1.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#pgwinstance2 install
	chartname="citm-ingress"
	podname="pgwinstance2"
	helm3 install pgwinstance2 -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$chartname/values_instance2.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#pgwinstance3 install
	chartname="citm-ingress"
	podname="pgwinstance3"
	helm3 install pgwinstance3 -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$chartname/values_instance3.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#pgwinstance4 install
	chartname="citm-ingress"
	podname="pgwinstance4"
	helm3 install pgwinstance4 -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$chartname/values_instance4.yaml
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw-psp install
	chartname="psp"
	podname="pgw-psp"
	helm3 install pgw-psp -n $pgwns $pgwInstallPath$chartname
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw-infracmn install
	chartname="infracommon"
	podname="pgw-infracmn"
	helm3 install pgw-infracmn -n $pgwns $pgwInstallPath$chartname
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw1-kafka install
	chartname="ckaf-kafka"
	podname="pgw1-kafka"
	helm3 install pgw1-kafka -n $pgwns $pgwInstallPath$chartname --wait --timeout 1200s
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw-pgwcas install
	chartname="pgwcas"
	podname="pgw-pgwcas"
	valuesyaml="infracommon/values.yaml"
	helm3 install pgw-pgwcas -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$valuesyaml --wait --timeout 1200s
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw-pgwbulk install
	chartname="pgwbulk"
	podname="pgw-pgwbulk"
	helm3 install pgw-pgwbulk -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$valuesyaml
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw-pgwcore install
	chartname="pgw"
	podname="pgw-pgwcore"
	helm3 install pgw-pgwcore -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$valuesyaml --wait --timeout 2700s
	result=$?
	checkInstallResult ${result} ${podname}
	#pgw-cma install
	chartname="clustermonitoragent"
	podname="pgw-cma"
	helm3 install pgw-cma -n $pgwns $pgwInstallPath$chartname -f $pgwInstallPath$chartname/values.yaml
	result=$?
	checkInstallResult ${result} ${podname}

    sleep 1m
}


prepareVipCrd(){
    kubectl -n $sdlns apply -f $1'oam-vip.yaml'
    kubectl -n $sdlns apply -f $1'app-vip.yaml'
    kubectl -n $sdlns apply -f $1'db-vip.yaml'
}

preparePgwVipCrd(){
    kubectl -n $pgwns apply -f $1'extoam1-vip.yaml'
    kubectl -n $pgwns apply -f $1'extoam2-vip.yaml'
    kubectl -n $pgwns apply -f $1'extoam4-vip.yaml'
	kubectl -n $pgwns apply -f $1'extapp3-vip.yaml'
	kubectl -n $pgwns apply -f $1'extprov1-vip.yaml'
	kubectl -n $pgwns apply -f $1'extprov2-vip.yaml'
}

checkHelmListStatus(){
    output=`helm3 list -n $1 | tail -n +2`
    OLD_IFS=$IFS
    IFS=$'\n'
    arr=($output)
    for i in ${arr[@]}
    do
    IFS="$OLD_IFS"
    items=($i)

    if [[ ${items[7]} == 'deployed' ]]; then
        echo "Successfully deployed ${items[0]} chart."
    else
        echo "Failed to deploy ${items[0]} chart."
        exit 1
    fi

    done
}

checkPodStatus(){
    output=`kubectl get pods -n $1 | tail -n +2`
    OLD_IFS=$IFS
    IFS=$'\n'
    arr=($output)
    for i in ${arr[@]}
    do
    IFS="$OLD_IFS"
    items=($i)
	str="${items[1]}"
	array=(${str//// })

    if [[ ${array[0]} == ${array[1]} ]]; then
        echo "Successfully deployed pod ${items[0]}, it running as ${array[0]}/${array[1]}."
    else
        echo "Failed to deploy pod ${items[0]}, it running as ${array[0]}/${array[1]}, will retry automaticlly."
        return 1
    fi

    done
	return 0
}

checkSpecPodsStatus(){
	for i in {0..4};
    do 
    checkPodStatus $1

	if [ $? -ne 0 ]; then 
	    echo "wait for pod ready, sleep 1 min";
		sleep 1m
		if [ $i -eq 4 ]; then echo "pods deployed failed, please check pods status";exit 1;fi
	else
	    echo "All pods are fully running, can execute next step"
		break 
	fi
    done
}

main(){
	#
	#pgwns=pgw-cet
	#path=/root/jiangjil/SDL_2250.0.2030/INSTALL_MEDIA/CHARTS/
	#pgwpath=/root/jiangjil/PGW_2250.0.2030/INSTALL_MEDIA/CHARTS/

	echo ${sdlns}
	echo ${pgwns}
    echo ${sdlInstallPath}
	echo ${product}

	if [[ ${product} == 'sdl' ]]; then
	    kubectl create namespace ${sdlns}
        prepareVipCrd $sdlCrdPath
	    sdlHelmNativeInstall
	    checkHelmListStatus $sdlns
	    checkSpecPodsStatus $sdlns
    else
	    kubectl create namespace ${pgwns}
        prepareVipCrd $pgwCrdPath
	    pgwHelmNativeInstall
	    checkHelmListStatus $pgwns
	    checkSpecPodsStatus $pgwns
    fi

}

main


