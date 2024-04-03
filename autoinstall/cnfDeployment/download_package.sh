#!/bin/bash
#### Download Package #############
PKG_DIR=$1
LOAD_NUM=$2
download_pkg(){
    
}

echo "pkg Dir is ${PKG_DIR}"
if [ ! -d "${PKG_DIR}" ]; then
        mkdir -p ${PKG_DIR}
        echo "${PKG_DIR} create finished"
fi
if [[ ! -d ${LOAD_NUM} ]] && [[ ! -f ${LOAD_NUM}.tar.gz ]]; then
    RELEASE=`echo ${LOAD_NUM}| awk -F '-' '{print $1}'|awk -F '_' '{print $2}'`
    echo "Downloading Package $aps_name_plus_update"
    BASE_URL="https://repo.lab.pl.alcatel-lucent.com/list/udm-generic-candidates/NREG_BUNDLE_COMMON/${RELEASE}/"
    aps_name_plus_update=`echo ${LOAD_NUM}| awk -F '-' '{print $2}'|awk -F '.' '{print $1}'`
    aps_name_plus_update="IMSDL"${aps_name_plus_update}".000"
    echo ${aps_name_plus_update}
    link=${BASE_URL}${aps_name_plus_update}"/"${LOAD_NUM}".tar.gz"
    cd ${PKG_DIR}
    echo "Downloading Package $link to ${PKG_DIR}"
    wget $link
    if [[ $? -eq 0 ]]; then
        echo "##  Downloading Package $aps_name_plus_update succesfully ##"
    else
        echo "##  Downloading Package $aps_name_plus_update failure ##"
        exit 1
    fi
fi
if [[ -f ${LOAD_NUM}.tar.gz ]]; then
### UnTAR Package #############
    cd ${PKG_DIR}
    tar xzvf "${LOAD_NUM}".tar.gz
    if [[ $? -eq 0 ]]; then
        echo "##  package ${LOAD_NUM}.tar.gz untar succesfully ##"
        rm -rf "${LOAD_NUM}".tar.gz
    else
        echo "##  package ${LOAD_NUM}.tar.gz untar failure  ##"
        exit 1
    fi
fi
if [[ -d ${LOAD_NUM} ]]; then
    echo "##  package is already downloaded"
fi
exit 0
