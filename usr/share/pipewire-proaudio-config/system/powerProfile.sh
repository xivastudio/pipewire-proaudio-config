#!/bin/bash

# sets whether it is running in flatpak
if [ -n "$FLATPAK_ID" ]; then
  exec='flatpak-spawn --host'
else
  exec=
fi

# check current status
check_state() {
  if $exec which powerprofilesctl >/dev/null 2>&1; then
    if [[ -z "$(grep performance <<< $($exec powerprofilesctl list))" ]];then
      echo ""
    elif [[ "$($exec powerprofilesctl get)" == "performance" ]];then
      echo "true"
    else
      echo "false"
    fi
  elif $exec which tuned-adm >/dev/null 2>&1; then
    if [[ -z "$(grep throughput-performance <<< $($exec tuned-adm list))" ]];then
      echo ""
    elif [[ "$($exec tuned-adm active | awk -F ': ' '{print $2}')" == "throughput-performance" ]];then
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
    if $exec which powerprofilesctl >/dev/null 2>&1; then
      $exec powerprofilesctl set performance
    elif $exec which tuned-adm >/dev/null 2>&1; then
      $exec tuned-adm profile throughput-performance
    fi
    exitCode=$?
  else
    if $exec which powerprofilesctl >/dev/null 2>&1; then
      $exec powerprofilesctl set balanced
    elif $exec which tuned-adm >/dev/null 2>&1; then
      $exec tuned-adm profile balanced
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
