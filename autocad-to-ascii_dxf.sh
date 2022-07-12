#!/bin/bash

# set -e

# debug commands
# set -x

# Launch virtual X server
if xdpyinfo -display :99 >/dev/null 2>&1; then
    :
else
    rm -rf /tmp/.X99-lock
    Xvfb :99 &
    while [ ! -e /tmp/.X11-unix/X99 ]; do sleep 0.1; done
fi

rm -rf /tmp/finish

# Debug with X11
# rm -rf /data/screenshot/
# mkdir -p /data/screenshot
# (
#     for i in {1..100}; do
#         if test -f /tmp/finish; then break; fi
#         DISPLAY=:99 xwd -root -silent | convert xwd:- png:/data/screenshot/screenshot_$i.png
#         echo $?
#     done
# ) &

# Launch converter
# export QT_DEBUG_PLUGINS=1
export DXF_ENCODING=UTF-8
export XDG_RUNTIME_DIR='/tmp/runtime-root'

# Display guide in X11
# DISPLAY=:99 ODAFileConverter --help

DISPLAY=:99 ODAFileConverter $1 $2 ACAD2018 DXF 0 1

touch /tmp/finish

# Kill virtual X server
kill $(pidof Xvfb)
