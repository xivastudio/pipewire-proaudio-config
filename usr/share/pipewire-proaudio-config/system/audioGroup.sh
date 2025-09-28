#!/bin/bash

# sets whether it is running in flatpak
if [ -n "$FLATPAK_ID" ]; then
  exec='flatpak-spawn --host --directory=/'
else
  exec=
fi

# check current status
check_state() {
  if [[ -n "$(grep audio <<< $($exec groups $(whoami)))" ]];then
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
      $exec pkexec groupadd audio
    fi
    $exec pkexec usermod -aG audio $(whoami)
    exitCode=$?
  else
    $exec pkexec gpasswd -d $(whoami) audio
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
