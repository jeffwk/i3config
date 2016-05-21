#!/bin/bash
pacaur -Sy > /dev/null
x=`pacaur -Qu | wc -l`
if [ $x -eq 0 ]; then
    echo "Up to date"
else
    echo "$x package updates"
fi
