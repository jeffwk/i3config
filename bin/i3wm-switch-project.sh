#!/bin/bash

wmctrl -c 'Select Project' || echo "$(zenity --title 'Select Project' --list --column 'Project Name' $(cat i3pslist))" > i3pwsvar
