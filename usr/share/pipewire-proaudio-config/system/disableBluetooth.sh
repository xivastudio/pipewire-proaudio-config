#!/bin/bash

# sets whether it is running in flatpak
if [ -n "$FLATPAK_ID" ]; then
  exec='flatpak-spawn --host --directory=/'
else
  exec=
fi

# check current status
check_state() {
  bluetoothState="$(LANG=C LANGUAGE=C timeout 0.1 $exec bluetoothctl show | grep "Powered:" | $exec awk '{print $2}')"
  if [[ "$bluetoothState" == "yes" ]];then
    echo "false"
  elif [[ "$bluetoothState" == "no" ]];then
    echo "true"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    timeout 2 $exec bluetoothctl power on
    exitCode=$?
  else
    timeout 2 $exec bluetoothctl power off
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
