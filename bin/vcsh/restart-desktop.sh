#!/bin/bash
pkill picom
pkill stalonetray
sleep 0.1 && picom -b --experimental-backends &
sleep 0.05 && stalonetray &
sleep 0.05 && restart-notify.sh &
sleep 0.05 && i3-msg 'focus tiling'
