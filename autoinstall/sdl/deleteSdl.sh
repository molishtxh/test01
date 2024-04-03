#!/bin/bash

#set -x
sdlns=$1
pgwns=$2
sdluninstallPath=$3
pgwuninstallPath=$4
sdlCrdPath=$5
pgwCrdPath=$6
product=$7

checkuninstallResult(){
    if [[ $1 -eq 0 ]]; then
        echo " Successfully execute helm uninstall $2 command."
    else
        echo "Warning: Cannot execute helm uninstall $2 command."
    fi
}

sdlHelmNativeUninstall(){	
	releaseList=("sdl-ntf" "sdl-oes" "sdl-cas" "sdl-rtdblookup" "sdl-disco" "sdl-diag" "sdl-storage" "sdl-access" "sdl1-kafka-ntf" "sdl1-kafka" "sdl-cmn" "sdl-psp" "sdl-multus" "sdldb" "sdlapp" "sdloam")
	for release in ${releaseList[@]}
    do
	helm3 uninstall $release -n $sdlns
	result=$?
	checkuninstallResult ${result} ${release}
    done
}

pgwHelmNativeUninstall(){
	releaseList=("pgw-cma" "pgw-pgwcore" "pgw-pgwbulk" "pgw-pgwcas" "pgw1-kafka" "pgw-infracmn" "pgw-psp" "pgwinstance4" "pgwinstance3" "pgwinstance2" "pgwinstance1")
	for release in ${releaseList[@]}
    do
	helm3 uninstall $release -n $pgwns
	result=$?
	checkuninstallResult ${result} ${release}
    done
}

deleteSdlVipCrd(){
    kubectl -n $sdlns delete -f $1'oam-vip.yaml'
    kubectl -n $sdlns delete -f $1'app-vip.yaml'
    kubectl -n $sdlns delete -f $1'db-vip.yaml'
}

deletePgwVipCrd(){
    kubectl -n $pgwns delete -f $1'extoam1-vip.yaml'
    kubectl -n $pgwns delete -f $1'extoam2-vip.yaml'
    kubectl -n $pgwns delete -f $1'extoam4-vip.yaml'
	kubectl -n $pgwns delete -f $1'extapp3-vip.yaml'
	kubectl -n $pgwns delete -f $1'extprov1-vip.yaml'
	kubectl -n $pgwns delete -f $1'extprov2-vip.yaml'
}

checkClearResult(){
    if [[ $1 -eq 0 ]]; then
        echo "Successfully clear $2."
    else
        echo "Warning: Cannot clear $2."
    fi
}

deletePods(){
    output=`kubectl get pods -n $1 | tail -n +2`
    OLD_IFS=$IFS
    IFS=$'\n'
    arr=($output)
    podList=()
    for i in ${arr[@]}
    do
    IFS="$OLD_IFS"
    items=($i)
    podList[${#podList[@]}]=${items[0]}
    done
    
    for pod in ${podList[@]}
    do
    kubectl delete pod $pod -n $1
	result=$?
	checkClearResult ${result} ${pod}
    done
}

deleteJobs(){
    output=`kubectl get jobs -n $1 | tail -n +2`
    OLD_IFS=$IFS
    IFS=$'\n'
    arr=($output)
    jobList=()
    for i in ${arr[@]}
    do
    IFS="$OLD_IFS"
    items=($i)
    jobList[${#jobList[@]}]=${items[0]}
    done
    
    for job in ${jobList[@]}
    do
    kubectl delete job $job -n $1
	result=$?
	checkClearResult ${result} ${job}
    done
}

deleteSecrets(){
    output=`kubectl get secret -n $1 | tail -n +2`
    OLD_IFS=$IFS
    IFS=$'\n'
    arr=($output)
    secretList=()
    for i in ${arr[@]}
    do
    IFS="$OLD_IFS"
    items=($i)
    secretList[${#secretList[@]}]=${items[0]}
    done
    
	for secret in ${secretList[@]}
    do
    if [[ $secret =~ 'default' ]];
    then 
        echo "default secret ${secret} won't be deleted"
    else
        kubectl delete secret $secret -n $1
	    result=$?
	    checkClearResult ${result} ${secret}
    fi
    done
}

deleteServiceAccount(){
    output=`kubectl get serviceaccount -n $1 | tail -n +2`
    OLD_IFS=$IFS
    IFS=$'\n'
    arr=($output)
    serviceaccountList=()
    for i in ${arr[@]}
    do
    IFS="$OLD_IFS"
    items=($i)
    serviceaccountList[${#serviceaccountList[@]}]=${items[0]}
    done
    
	for serviceaccount in ${serviceaccountList[@]}
    do
    if [[ $serviceaccount =~ 'default' ]];
    then 
        echo "default serviceaccount ${serviceaccount} won't be deleted"
    else
        kubectl delete serviceaccount $serviceaccount -n $1
	    result=$?
	    checkClearResult ${result} ${serviceaccount}
    fi
    done
}

clearLab(){
	deletePods $1
	deleteJobs $1
	deleteSecrets $1
	deleteServiceAccount $1
    kubectl delete pvc -n $1 --all
	kubectl delete configmaps  -n $1 --all
	kubectl delete VirtualIPClass  -n $1 --all
}

main(){
	echo ${sdlns}
	echo ${pgwns}
    echo ${sdluninstallPath}
	echo ${product}

    if [[ ${product} == 'sdl' ]]; then
        sdlHelmNativeUninstall
		deleteSdlVipCrd $sdlCrdPath
		clearLab $sdlns
    else
        pgwHelmNativeUninstall
		deletePgwVipCrd $pgwCrdPath
		clearLab $pgwns
    fi

}

main


