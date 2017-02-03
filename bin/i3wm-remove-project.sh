#!/bin/bash

wmctrl -c 'Delete Space Name:' || pname=$(zenity --title 'Delete Space Name:' --entry)
sed -i /"$pname"$/d i3pslist
