#!/usr/bin/env bash

# check if it is running as root, if not use sudo
if [ "$UID" -eq 0 ]; then
  sudo=
else
  sudo=sudo
fi

# install dependencies
$sudo dnf install git zenity -y

# If the repository already exists, update it. If not, clone it.
if [ -d "usr" ]; then
  git pull
else
  git clone https://github.com/biglinux/pipewire-proaudio-config.git .
fi

# copy usr/ to /
$sudo cp -rf usr/ /

