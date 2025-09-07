#!/bin/bash

# check current status
check_state() {
  if which powerprofilesctl >/dev/null 2>&1; then
    if [[ -z "$(grep performance <<< $(powerprofilesctl list))" ]];then
      echo ""
    elif [[ "$(powerprofilesctl get)" == "performance" ]];then
      echo "true"
    else
      echo "false"
    fi
  elif which tuned-adm >/dev/null 2>&1; then
    if [[ -z "$(grep throughput-performance <<< $(tuned-adm list))" ]];then
      echo ""
    elif [[ "$(tuned-adm active | awk -F ': ' '{print $2}')" == "throughput-performance" ]];then
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
    if which powerprofilesctl >/dev/null 2>&1; then
      powerprofilesctl set performance
    elif which tuned-adm >/dev/null 2>&1; then
      tuned-adm profile throughput-performance
    fi
    exitCode=$?
  else
    if which powerprofilesctl >/dev/null 2>&1; then
      powerprofilesctl set balanced
    elif which tuned-adm >/dev/null 2>&1; then
      tuned-adm profile balanced
    fi
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
