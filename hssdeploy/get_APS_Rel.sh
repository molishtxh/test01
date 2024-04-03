#!/bin/bash
## example: sh get_APS_Rel.sh NREG_24.03-24030022
#set -x
APS=`echo $1|awk -F - '{printf $2}'`
Rel_1=`echo ${APS}|cut -c 1-2`
Len=${#APS}
if [[ $Len = 7 ]];then
Rel_2=`echo ${APS}|cut -c 3`
Rel_3=`echo ${APS}|cut -c 4-7`
  if [[ $Rel_1 = "23" ]] && [[ `echo ${APS}|cut -c 3-4` = "11" ]];then
    Rel_2=`echo ${APS}|cut -c 3-4`
    Rel_3=`echo ${APS}|cut -c 5-7`
  fi
elif [[ $Len = 8 ]];then
Rel_2=`echo ${APS}|cut -c 3-4`
Rel_3=`echo ${APS}|cut -c 5-8`
else
echo "APS length is $Len and wrong, exit.."
exit 1
fi
Rel_2_int=`echo $Rel_2|bc`
Rel_3_int=`echo $Rel_3|bc`
if [[ $Rel_2 = "07" ]];then
Rel_2=7
fi
:<<!
echo "Rel_1 is: $Rel_1"
echo "Rel_2 is: $Rel_2"
echo "Rel_3 is: $Rel_3"
echo "Rel_2_int is: $Rel_2_int"
echo "Rel_3_int is: $Rel_3_int"
!
