FROM opensuse/tumbleweed

#Install latest patches
RUN zypper up

RUN zypper in --help

RUN zypper --non-interactive in --no-recommends \
    bash \
    wget \
    xvfb-run

RUN mkdir -p /openindoor
WORKDIR /openindoor

RUN zypper --non-interactive in --no-recommends \
    fontconfig libICE6 libQt5Core5 libQt5DBus5 libQt5Gui5 libQt5Network5 \
    libQt5Widgets5 libSM6 libdouble-conversion3 libevdev2 libfontconfig1 \
    libgobject-2_0-0 libgraphite2-3 libgudev-1_0-0 libharfbuzz0 libinput10 \
    libjpeg8 libmtdev1 libpcre2-16-0 libts0 \
    libwacom-data libwacom2 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-render0 libxcb-shape0 libxcb-shm0 \
    libxcb-util1 libxcb-xinerama0 libxcb-xinput0 libxcb-xkb1 \
    libxkbcommon-x11-0 libxkbcommon0 timezone

RUN wget --no-check-certificate \
    https://download.opendesign.com/guestfiles/Demo/ODAFileConverter_QT5_lnxX64_7.2dll_21.11.rpm
RUN zypper --non-interactive in --no-recommends --allow-unsigned-rpm \
    ODAFileConverter_QT5_lnxX64_7.2dll_21.11.rpm

RUN zypper --non-interactive in --no-recommends \
    gdal

RUN zypper --non-interactive in --no-recommends \
    python3 python3-Flask python3-pip

COPY ./requirements.txt /openindoor/requirements.txt
RUN pip install -r requirements.txt

COPY ./autocad-to-gis.py /openindoor/autocad-to-gis.py
COPY ./autocad-to-gis.sh /openindoor/autocad-to-gis.sh
RUN chmod +x /openindoor/autocad-to-gis.sh
RUN chmod +x /openindoor/autocad-to-gis.py

# ENV FLASK_APP="/openindoor/autocad-to-gis.py"
# ENV FLASK_ENV="development"

# CMD flask run --host=0.0.0.0
CMD /openindoor/autocad-to-gis.py

