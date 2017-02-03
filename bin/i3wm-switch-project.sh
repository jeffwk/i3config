#!/bin/bash

cp -f i3pwsvar i3pwslast
wmctrl -c 'Select Project' || echo "$(zenity --title 'Select Project' --list --column 'Project Name' $(cat i3pslist))" > i3pwsvar
i3-msg workspace $(cat i3pwsvar)_1
