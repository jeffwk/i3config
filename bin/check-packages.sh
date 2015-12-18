#!/bin/bash
x=`yaourt -Qua | wc -l`
if [ $x -eq 0 ]; then
    echo "Up to date"
else
    echo "$x package updates"
fi
