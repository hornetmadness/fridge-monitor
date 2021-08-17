#!/usr/bin/env bash
#Created by Erik Mathis 08/2021
#hornetmadness@gmail.com

#this script reads the results file from fridge-monitor.py 
#and exits with the temperature as the exit code for a monit
#service to monitor

file=${RESULTS_FILE:-"/run/user/1000/temp_results"}

ecode=$(jq -r '.avg|tonumber|floor' ${file} || echo 1)
cat ${file}
exit ${ecode}
