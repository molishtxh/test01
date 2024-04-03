#!/usr/bin/bash
hostname=`hostname`
while true
do
sar_cpu=`tail -20 sar_cpu |awk '{print $9}'`
sar_mem=`tail -20 sar_mem |awk '{print $6}'`
sum_cpu=0
sum_mem=0
for i in $sar_cpu;do
sum_cpu=`echo "$sum_cpu+$i"|bc`
done
for i in $sar_mem;do
sum_mem=`echo "$sum_mem+$i"|bc`
done
sum_cpu=`echo "scale=2;$sum_cpu/20"|bc`
sum_cpu=`echo "scale=2;100-$sum_cpu"|bc`
sum_mem=`echo "scale=2;$sum_mem/20"|bc`

date|awk '{printf $4"\t"}' >> cpu_${hostname}.txt
echo $sum_cpu >> cpu_${hostname}.txt

date|awk '{printf $4"\t"}' >> mem_${hostname}.txt
echo $sum_mem >> mem_${hostname}.txt

sleep 5
done
