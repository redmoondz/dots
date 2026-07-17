#!/bin/bash

if pgrep -x voxtype > /dev/null; then
    pkill -x voxtype
    sleep 0.3
    pkill -f voxtype-osd-gtk4 2>/dev/null
    notify-send "Voxtype" "Disabled" -i microphone-sensitivity-muted-symbolic
else
    setsid voxtype > /dev/null 2>&1 &
    disown
    notify-send "Voxtype" "Enabled" -i microphone-sensitivity-high-symbolic
fi
