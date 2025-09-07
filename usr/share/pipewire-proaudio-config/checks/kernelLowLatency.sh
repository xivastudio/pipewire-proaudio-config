#!/bin/bash

# check current status
if [[ -e "/proc/config.gz" ]] && [[ -n "$(zgrep CONFIG_HIGH_RES_TIMERS=y /proc/config.gz)" ]];then
  echo "true"
elif [[ -e "/proc/config.gz" ]] && [[ -n "$(zgrep CONFIG_HIGH_RES_TIMERS=y /proc/config.gz)" ]];then
  echo "false"
fi
