#!/bin/sh

echo '{"version":1}'

echo '['

echo '[],'

exec conky -c $HOME/.i3/conky/conkyrc 2> /dev/null
