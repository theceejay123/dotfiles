#!/bin/sh
# shell script to prepend i3status with more stuff

i3status | while :
do
    read line
    status="M: $(spotistat) | $line"
    #modstatus=$(echo $status | sed 's/|/ /g')
    # That last line, if uncommented, replaces the pipe separators with an em space
    echo $modstatus || exit 1
done