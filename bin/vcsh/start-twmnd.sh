#!/bin/bash

killall twmnd 2> /dev/null ; sleep 0.25
killall -9 twmnd 2> /dev/null ; sleep 0.25
twmnd & sleep 0.5
twmnc -t "twmnd" -c "started" -d 2000
