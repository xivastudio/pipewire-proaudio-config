#!/bin/bash

# check current status
if [[ -n "$(zgrep CONFIG_HIGH_RES_TIMERS=y /proc/config.gz)" ]] || [[ -n "$(grep CONFIG_HIGH_RES_TIMERS=y /boot/config-$(uname -r))" ]];then
  echo "true"
elif [[ -z "$(zgrep CONFIG_HIGH_RES_TIMERS=y /proc/config.gz)" ]] || [[ -z "$(grep CONFIG_HIGH_RES_TIMERS=y /boot/config-$(uname -r))" ]];then
  echo "false"
fi
