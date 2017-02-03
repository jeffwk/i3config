#!/bin/bash
pacaur -Sy > /dev/null
x=`pacaur -Qu | wc -l`
echo "$x"
