#!/bin/bash

killall twmnd 2> /dev/null ; sleep 0.1
killall -9 twmnd 2> /dev/null ; sleep 0.1
twmnd & sleep 0.5
twmnc -t "twmnd" -c "started" -d 2000
