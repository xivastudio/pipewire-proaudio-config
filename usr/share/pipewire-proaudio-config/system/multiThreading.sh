#!/bin/bash

# sets whether it is running in flatpak
if [ -n "$FLATPAK_ID" ]; then
  exec='flatpak-spawn --host --directory=/'
else
  exec=
fi

# check current status
check_state() {
  if [[ "$(cat /sys/devices/system/cpu/smt/control)" != "on" ]] && [[ "$(cat /sys/devices/system/cpu/smt/control)" != "off" ]];then
    echo ""
  elif [[ "$(cat /sys/devices/system/cpu/smt/control)" == "off" ]];then
    echo "true"
  elif [[ "$(cat /sys/devices/system/cpu/smt/control)" == "on" ]];then
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    echo off | $exec pkexec tee /sys/devices/system/cpu/smt/control
    exitCode=$?
  else
    echo on | $exec pkexec tee /sys/devices/system/cpu/smt/control
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
