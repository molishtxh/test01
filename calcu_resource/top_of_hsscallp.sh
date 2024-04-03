#!/bin/bash
## app list: hsscallp, hlrcallp, arpf, dlb, ss7
ns="ptreg"
app1="hsscallp"
app2="hlrcallp"
app3=""
app4=""
udmenvoy_monitor="true"
logfile_name="hss_top.log"

caculate_top(){
app=${1:-hsscallp}
if [[ $app = "hsscallp" ]];then
app_container_cpu_req=6000
app_container_mem_req=26000
app_udmenvoy_cpu_req=500
app_udmenvoy_mem_req=1200
elif [[ $app = "hlrcallp" ]];then
app_container_cpu_req=6000
app_container_mem_req=9050
app_udmenvoy_cpu_req=300
app_udmenvoy_mem_req=400
elif [[ $app = "arpf" ]];then
app_container_cpu_req=6000
app_container_mem_req=6000
app_udmenvoy_cpu_req=1300
app_udmenvoy_mem_req=1200
elif [[ $app = "dlb" ]];then
app_container_cpu_req=5000
app_container_mem_req=5600
app_udmenvoy_cpu_req=2300
app_udmenvoy_mem_req=1200
elif [[ $app = "ss7" ]];then
app_container_cpu_req=10000
app_container_mem_req=11000
app_udmenvoy_cpu_req=100
app_udmenvoy_mem_req=300
fi
app_container_cpu_sum=0
app_container_mem_sum=0
app_udmenvoy_cpu_sum=0
app_udmenvoy_mem_sum=0
pod_count_app=0
pod_list=`kubectl get pod -n $ns |grep $app|awk '{if($3=="Running"){print$1}}'`
echo "-----------------------------------------------------------------------" >> $logfile_name
for pod in $pod_list;do
pod_count_app=$(($pod_count_app+1))
pod_top_data=`kubectl top pod $pod --containers -n $ns --use-protocol-buffers`
app_container_cpu=`echo "$pod_top_data"|grep " ${app} "|awk '{printf$3}'|sed -r 's/m//g'`
app_container_cpu_sum=$(($app_container_cpu_sum+$app_container_cpu))
app_container_mem=`echo "$pod_top_data"|grep " ${app} "|awk '{printf$4}'|sed -r 's/Mi//g'`
app_container_mem_sum=$(($app_container_mem_sum+$app_container_mem))
if [[ $udmenvoy_monitor = "true" ]];then
container_udmenvoy_cpu=`echo "$pod_top_data"|grep " udmenvoy "|awk '{printf$3}'|sed -r 's/m//g'`
app_udmenvoy_cpu_sum=$(($app_udmenvoy_cpu_sum+$container_udmenvoy_cpu))
container_udmenvoy_mem=`echo "$pod_top_data"|grep " udmenvoy "|awk '{printf$4}'|sed -r 's/Mi//g'`
app_udmenvoy_mem_sum=$(($app_udmenvoy_mem_sum+$container_udmenvoy_mem))
fi
done
if [[ $app = "dlb" ]] || [[ $app = "ss7" ]];then
pod_count_app=1
fi
date|awk '{printf $4"\t'${app}'_cpu_avg"}' >> $logfile_name
echo "$app_container_cpu_sum/$pod_count_app"|bc|awk '{printf"\t"$1"m"}' >> $logfile_name
echo "scale=2;${app_container_cpu_sum}*100/($app_container_cpu_req*$pod_count_app)"|bc|awk '{printf "\t%.2f%\n",$1}' >> $logfile_name
date|awk '{printf $4"\t'${app}'_mem_avg"}' >> $logfile_name
echo "$app_container_mem_sum/$pod_count_app"|bc|awk '{printf"\t"$1"Mi"}' >> $logfile_name
echo "scale=2;${app_container_mem_sum}*100/($app_container_mem_req*$pod_count_app)"|bc|awk '{printf "\t%.2f%\n",$1}' >> $logfile_name
if [[ $udmenvoy_monitor = "true" ]];then
echo "--------------------------------" >> $logfile_name
date|awk '{printf $4"\t'${app}'_udmenvoy_cpu"}' >> $logfile_name
echo "$app_udmenvoy_cpu_sum/$pod_count_app"|bc|awk '{printf"\t"$1"m"}' >> $logfile_name
echo "scale=2;${app_udmenvoy_cpu_sum}*100/($app_udmenvoy_cpu_req*$pod_count_app)"|bc|awk '{printf "\t%.2f%\n",$1}' >> $logfile_name
date|awk '{printf $4"\t'${app}'_udmenvoy_mem"}' >> $logfile_name
echo "$app_udmenvoy_mem_sum/$pod_count_app"|bc|awk '{printf"\t"$1"Mi"}' >> $logfile_name
echo "scale=2;${app_udmenvoy_mem_sum}*100/($app_udmenvoy_mem_req*$pod_count_app)"|bc|awk '{printf "\t%.2f%\n",$1}' >> $logfile_name
fi
}

##check if log size is greater than 20M
dir_list=`pwd $0`
log_size=`ls -l $dir_list|grep "$logfile_name$"|awk '{printf$5}'`
if [[ -f ./$logfile_name ]] && [ $log_size -gt 20000000 ];then
  mv $logfile_name $logfile_name.bak`date "+%Y-%m-%d_%H_%M_%S"`
fi

while true;do
date >> $logfile_name
caculate_top $app1
if [[ $app2 != "" ]];then
caculate_top $app2
fi
if [[ $app3 != "" ]];then
caculate_top $app3
fi
if [[ $app4 != "" ]];then
caculate_top $app4
fi
echo "==============================================================================" >> $logfile_name
sleep 30
done
