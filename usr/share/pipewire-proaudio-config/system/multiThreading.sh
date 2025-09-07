#!/bin/bash

# check current status
check_state() {
  if [[ "$(cat /sys/devices/system/cpu/smt/control)" != "on" ]] && [[ "$(cat /sys/devices/system/cpu/smt/control)" != "off" ]];then
    echo ""
  elif [[ "$(cat /sys/devices/system/cpu/smt/control)" == "off" ]];then
    echo "true"
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    echo off | pkexec tee /sys/devices/system/cpu/smt/control
    exitCode=$?
  else
    echo on | pkexec tee /sys/devices/system/cpu/smt/control
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
