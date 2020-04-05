#!/bin/bash
i3-msg 'move workspace to output right'
sleep 0.1
pkill -9 stalonetray
sleep 0.1
stalonetray &
