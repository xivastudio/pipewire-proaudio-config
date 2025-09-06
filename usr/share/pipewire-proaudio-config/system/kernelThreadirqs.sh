#!/bin/bash

# check current status
check_state() {
  if [[ -e "/proc/config.gz" ]] && [[ -n "$(zgrep CONFIG_PREEMPT_RT=y /proc/config.gz)" ]];then
    echo ""
  elif [[ -e "/proc/config.gz" ]] && [[ -n "$(zgrep CONFIG_IRQ_FORCED_THREADING=y /proc/config.gz)" ]];then
    if [[ -n "$(grep "threadirqs" /proc/cmdline)" ]];then
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
    pkexec $PWD/system/kernelThreadirqsRun.sh "enable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
    exitCode=$?
  else
    pkexec $PWD/system/kernelThreadirqsRun.sh "disable" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
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
