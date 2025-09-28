#!/bin/bash

# sets whether it is running in flatpak
if [ -n "$FLATPAK_ID" ]; then
  exec='flatpak-spawn --host --directory=/'
else
  exec=
fi

# check current status
check_state() {
  if [[ "$(LANG=C LANGUAGE=C $exec nmcli radio wifi)" == "enabled" ]];then
    echo "false"
  elif [[ "$(LANG=C LANGUAGE=C $exec nmcli radio wifi)" == "disabled" ]];then
    echo "true"
  fi
}

# change the state
toggle_state() {
  new_state="$1"
  if [[ "$new_state" == "true" ]];then
    $exec nmcli radio wifi on
    exitCode=$?
  else
    $exec nmcli radio wifi off
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
