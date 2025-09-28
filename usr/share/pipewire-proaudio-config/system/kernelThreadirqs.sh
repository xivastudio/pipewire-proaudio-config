#!/bin/bash

# sets whether it is running in flatpak
if [ -n "$FLATPAK_ID" ]; then
  exec='flatpak-spawn'
else
  exec=
fi

# check current status
check_state() {
  if [[ -e "/proc/config.gz" ]];then
    if [[ "$(zgrep -e CONFIG_IRQ_FORCED_THREADING=y -e CONFIG_PREEMPT_RT=y /proc/config.gz | wc -l)" -eq "2" ]];then
      echo "true_disabled"
    elif [[ "$(zgrep -e CONFIG_IRQ_FORCED_THREADING=y -e CONFIG_PREEMPT_RT=y /proc/config.gz | wc -l)" -eq "0" ]];then
      echo ""
    elif [[ -n "$(zgrep -e CONFIG_IRQ_FORCED_THREADING=y /proc/config.gz)" ]] && [[ -n "$(grep "threadirqs" /proc/cmdline)" ]];then
      echo "true"
    else
      echo "false"
    fi
  elif [[ -e "/boot/config-$(uname -r)" ]];then
    if [[ "$(grep -e CONFIG_IRQ_FORCED_THREADING=y -e CONFIG_PREEMPT_RT=y /boot/config-$(uname -r) | wc -l )" -eq "2" ]];then
      echo "true_disabled"
    elif [[ "$(grep -e CONFIG_IRQ_FORCED_THREADING=y -e CONFIG_PREEMPT_RT=y /boot/config-$(uname -r) | wc -l )" -eq "0" ]];then
      echo ""
    elif [[ -n "$(grep CONFIG_IRQ_FORCED_THREADING=y /boot/config-$(uname -r))" ]] && [[ -n "$(grep "threadirqs" /proc/cmdline)" ]];then
      echo "true"
    else
      echo "false"
    fi
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    $exec pkexec $PWD/system/kernelThreadirqsRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  else
    $exec pkexec $PWD/system/kernelThreadirqsRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  fi
  exit $exitCode
}

# Executes the function based on the parameter
case "$1" in
    "check")
        check_state
        ;;
    "toggle")
        toggle_state "$2"
        ;;
    *)
        echo "Use: $0 {check|toggle} [true|false]"
        echo "  check          - Check current status"
        echo "  toggle <state> - Changes to the specified state"
        exit 1
        ;;
esac
