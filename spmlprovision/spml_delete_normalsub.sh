#!/bin/bash
k=1100000000
work_dir=$(cd `dirname $0`; pwd)
target_dir="/srv/sftp/bulk-sftp-DEFAULT"
mkdir -p ${work_dir}/backup_delete
chown provgw:provgw ${work_dir}/backup_delete
echo "==last sub.res time== "`ls -lhtr ${target_dir}/outbox/sub_*|tail -1` >> ${work_dir}/log_provision
rm -rf ${target_dir}/outbox/sub_* ${work_dir}/backup_delete/*
for (( i1=0; i1<${1}; i1+=50000 ))
do
start_sub=$(($k+$i1))
cat << EOF > ${work_dir}/backup_delete/sub_delete${1}_${start_sub}.spml
<?xml version="1.0" encoding="UTF-8"?>
<spml:batchRequest
    onError="exit_commit"
    processing="sequential"
    xmlns:spml="urn:siemens:names:prov:gw:SPML:2:0"
    xmlns:subscriber="urn:siemens:names:prov:gw:UNIFIED_SUB_3GPPHSS:1:0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<version>UNIFIED_SUB_3GPPHSS_v10</version>
EOF
for (( i2=0; i2<50000; i2++ ))
do
j=$(($k+$i1+$i2))
if [ $j -ge $(($k+${1})) ];then
break
fi
cat << EOF >> ${work_dir}/backup_delete/sub_delete${1}_${start_sub}.spml
        <request xsi:type="spml:DeleteRequest">
            <version>UNIFIED_SUB_3GPPHSS_v10</version>
            <objectclass>Subscriber</objectclass>
            <identifier>26375${j}</identifier>
        </request>
EOF
done
cat << EOF >> ${work_dir}/backup_delete/sub_delete${1}_${start_sub}.spml
</spml:batchRequest>
EOF
chown provgw:provgw ${work_dir}/backup_delete/sub_delete${1}_${start_sub}.spml
echo "==========sub_delete${1}_${start_sub}.spml start time========== "`date "+%Y-%m-%d %H:%M"` >> ${work_dir}/log_provision
su - provgw -c "cp ${work_dir}/backup_delete/sub_delete${1}_${start_sub}.spml ${target_dir}/inbox/"
done