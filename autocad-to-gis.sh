#!/bin/bash

# set -e
set -x

rm -rf /tmp/.X99-lock
Xvfb :99 -screen 0 1024x768x16 &
while [ ! -e /tmp/.X11-unix/X99 ]; do sleep 0.1; done

export DXF_ENCODING=UTF-8
export XDG_RUNTIME_DIR='/tmp/runtime-root'
# export DISPLAY=:99.0
# for folder in $(find /data -type f -name "*.dwg" -exec dirname {} \; | sort -u); do
    # DISPLAY=:99.0 ODAFileConverter \
    #     "${folder}" \
    #     "${folder}" \
    #     ACAD2018 DXF 1 1 "*.dwg"
#         # ACAD2015 DXF 1 1 "*.dwg"
#         # ACAD2000 DXF 1 1 "*.dwg"
#         # ACAD2014 DXF 1 1 "*.dwg"
#         # ACAD12 DXF 1 1 "*.dwg"
#         # ACAD2010 DXF 1 1 "*.dwg"
# done

DISPLAY=:99.0 ODAFileConverter $1 $2 ACAD2018 DXF 1 1 "*.dxf"


# export FLASK_APP=/openindoor/autocad-to-gis.py
# export FLASK_ENV=development

# /openindoor/autocad-to-gis.py