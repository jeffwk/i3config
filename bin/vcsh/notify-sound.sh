#!/bin/bash
echo $* | cat > ~/sound-args.txt

mpv --volume=30 ~/.config/twmn/ping.mp3 > /dev/null 2> /dev/null
true
