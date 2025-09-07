#!/bin/bash

# check current status
if [[ -e "/proc/config.gz" ]] && [[ -n "$(zgrep CONFIG_HIGH_RES_TIMERS=y /proc/config.gz)" ]] || [[ -e "/boot/config-$(uname -r)" ]] && [[ -n "$(grep CONFIG_HIGH_RES_TIMERS=y /boot/config-$(uname -r))" ]];then
  echo "true"
elif [[ -e "/proc/config.gz" ]] && [[ -z "$(zgrep CONFIG_HIGH_RES_TIMERS=y /proc/config.gz)" ]] || [[ -e "/boot/config-$(uname -r)" ]] && [[ -z "$(grep CONFIG_HIGH_RES_TIMERS=y /boot/config-$(uname -r))" ]];then
  echo "false"
fi
