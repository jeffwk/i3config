#!/bin/bash

wmctrl -c 'Add Space Name:' || pname=$(zenity --title 'Add Space Name:' --entry)

[[ -z $pname ]] || egrep -q ''"$pname"'$' i3pslist || echo "$pname" | sed 's/ /_/g'>> i3pslist;echo $(sort i3pslist) > i3pslist
