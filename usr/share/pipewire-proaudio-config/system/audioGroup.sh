#!/bin/bash

# check current status
check_state() {
  if [[ -n "$(grep audio <<< $(groups $(whoami)))" ]];then
    echo "true"
  else
    echo "false"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    if [[ -z "$(getent group audio)" ]];then
      pkexec groupadd audio
    fi
    pkexec usermod -aG audio $(whoami)
    exitCode=$?
  else
    pkexec gpasswd -d $(whoami)
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
