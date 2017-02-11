#!/bin/bash
use_yaourt=
if [[ $use_yaourt ]] ; then
    yaourt -Sya > /dev/null
    x=`yaourt -Qua | wc -l`
else
    pacaur -Sy > /dev/null
    x=`pacaur -Qu | wc -l`
fi
echo "$x"
