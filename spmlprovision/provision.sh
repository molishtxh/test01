#!/bin/bash
work_dir=$(cd `dirname $0`; pwd)
target_dir="/srv/sftp/bulk-sftp-DEFAULT"
rm -rf ${target_dir}/outbox/${1}*
#chown provgw:provgw ${work_dir}
chown provgw:provgw ${work_dir}/${1}
su - provgw -c "cp ${work_dir}/${1} ${target_dir}/inbox/"