#!/bin/bash

# check current status
if [[ -e "/usr/bin/pw-jack" ]];then
  echo "true"
else
  echo "false"
fi
