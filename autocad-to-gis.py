#!/usr/bin/env python3

import logging
import fiona
import geopandas
import json
import os
import pathlib
import shutil
import subprocess
import sys
import traceback
import uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

logger = logging.getLogger('autocad-to-gis')
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='log/autocad-to-gis.log', filemode='w')
# logger.info('start logger')

# #!/bin/bash

# set -e
# set -x

# rm -rf /tmp/.X99-lock
# Xvfb :99 -screen 0 1024x768x16 &
# while [ ! -e /tmp/.X11-unix/X99 ]; do sleep 0.1; done

# export DXF_ENCODING=UTF-8
# export XDG_RUNTIME_DIR='/tmp/runtime-root'

# for folder in $(find /data -type f -name "*.dwg" -exec dirname {} \; | sort -u); do
#     DISPLAY=:99.0 ODAFileConverter \
#         "${folder}" \
#         "${folder}" \
#         ACAD2018 DXF 1 1 "*.dwg"
#         # ACAD2015 DXF 1 1 "*.dwg"
#         # ACAD2000 DXF 1 1 "*.dwg"
#         # ACAD2014 DXF 1 1 "*.dwg"
#         # ACAD12 DXF 1 1 "*.dwg"
#         # ACAD2010 DXF 1 1 "*.dwg"
# done

# echo "finished !"

UPLOAD_FOLDER = '/data'
ALLOWED_EXTENSIONS = {'dwg', 'dxf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# curl -F "file=@autocad-to-gis/data/kingconf/sett_22-11_14.dxf" \
#     https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/-0.8782/47.0545/0.0/0.0/45.0/0.5
@app.route('/api/autocad-to-gis/convert/<float(signed=True):lng>/<float(signed=True):lat>/<float(signed=True):xoff>/<float(signed=True):yoff>/<float(signed=True):rot>/<float(signed=True):scale>', methods=['POST'])
@app.route('/api/autocad-to-gis/convert/<float(signed=True):lng>/<float(signed=True):lat>', methods=['POST'])
def convert_all(lng, lat, xoff = 0, yoff = 0, rot = 0, scale = 1):
    # Get data as a file
    if 'file' not in request.files:
        logger.error('No input file')
        flash('No file part')
        return app.response_class(status=400)
    file = request.files['file']

    # logging.info('file.filename:', file.filename)
    if file.filename == '':
        flash('No selected file')
        return app.response_class(status=400)
    if not (file and allowed_file(file.filename)):
        return app.response_class(status=400)

    print('file.filename:', file.filename, file=sys.stderr, flush=True)
    logger.info('file.filename: %s', file.filename)

    filename = secure_filename(file.filename)
    file_base = os.path.splitext(filename)[0]
    file_ext = os.path.splitext(filename)[1]
    file_uuid = uuid.uuid4().hex
    # AutoCAD file
    autocad_folder = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file_uuid,
        "autocad",
    )
    pathlib.Path(autocad_folder).mkdir(parents=True, exist_ok=True)
    autocad_path = os.path.join(
        autocad_folder,
        filename
    )
    logger.debug('Original file: %s', autocad_path)

    # ASCII DXF
    ascii_dxf_folder = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file_uuid,
        "ascii_dxf",
    )
    pathlib.Path(ascii_dxf_folder).mkdir(parents=True, exist_ok=True)
    ascii_dxf_path = os.path.join(
        ascii_dxf_folder,
        file_base + ".dxf"
    )
    logger.debug('DXF ASCII file: %s', ascii_dxf_path)

    # geojson file
    geojson_folder = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file_uuid,
        "geojson",
    )
    pathlib.Path(geojson_folder).mkdir(parents=True, exist_ok=True)
    geojson_path = os.path.join(
        geojson_folder,
        file_base + ".geojson"
    )
    logger.debug('Geojson to write: %s', geojson_path)

    file.save(autocad_path)
    
    # Convert Autocad data to ASCII DXF
    print('autocad_path:', autocad_path, file=sys.stderr, flush=True)
    cmd = [
        "/openindoor/autocad-to-ascii_dxf.sh",
        autocad_folder,
        ascii_dxf_folder,
    ]
    print(cmd, file=sys.stderr, flush=True)
    logger.info('cmd: %s', cmd)
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
    )
        # shell=True,
        # capture_output=True,
        # text=True,
        # stdout=subprocess.PIPE,
        # env={
        #     "DXF_ENCODING": "UTF-8",
        #     "XDG_RUNTIME_DIR": "/tmp/runtime-root",
        #     "DISPLAY": ":99.0",
        # }
    # )

    ogrinfo = subprocess.run(
        [
            "ogrinfo",
            "-ro",
            ascii_dxf_path
        ],
        stdout = subprocess.PIPE
    )
    print('ogrinfo:', ogrinfo, file=sys.stderr, flush=True)
    logger.info('ogrinfo: %s', ogrinfo)

    # print(result.stderr, file=sys.stderr)
    if (result.returncode != 0):
        print("returncode:", result.returncode, file=sys.stderr, flush=True)
        return app.response_class(
            response=json.dumps(
                {"returncode": result.returncode}
            ),
            status=400,
            mimetype='application/json'
        )
    # print(result.stderr, file=sys.stderr)

    # Convert ASCII DXF file to geojson

    # lambert_93 = "EPSG:27561"
# https://gdal.org/drivers/vector/dxf.html
# GDAL writes DXF files with measurement units set to “Imperial - Inches”. If you need to change the units, edit the $MEASUREMENT and $INSUNITS variables in the header template.
    crs = "+proj=lcc" \
    " +lat_1=" + str(lat) + "" \
    " +lat_0=" + str(lat) + "" \
    " +lon_0=" + str(lng) + "" \
    " +k_0=0.999877341" \
    " +a=6378249.2" \
    " +b=6356515" \
    " +units=m" \
    " +no_defs"

    # " +towgs84=-168,-60,320,0,0,0,0" \
    # " +pm=paris" \
    # " +x_0=600000" \
    # " +y_0=200000" \

    print("crs:", crs, file=sys.stderr)

    # crs = '+proj=lcc +lat_1=' + str(lat) + ' +units=m +no_defs'
    try:
        ascii_dxf = geopandas.read_file(
            ascii_dxf_path,
            encoding='utf-8',
            env = fiona.Env(DXF_ENCODING="UTF-8")
        )
        print('ascii_dxf.crs:', ascii_dxf.crs, file=sys.stderr)
        ascii_dxf.set_crs(
            crs = crs,
            inplace = True
        )
        print('ascii_dxf.crs:', ascii_dxf.crs, file=sys.stderr)
        logger.info('Applied crs: %s', ascii_dxf.crs)

        # total_bounds = ascii_dxf.total_bounds
        # print('total_bounds:', total_bounds, file=sys.stderr)
        # print('total_bounds[0]:', total_bounds[0], file=sys.stderr)

        total_bounds = ascii_dxf.total_bounds
        ascii_dxf = ascii_dxf.rotate(
            angle = rot,
            origin=(
                total_bounds[2] - total_bounds[0],
                total_bounds[3] - total_bounds[1]
            )
        )

        ascii_dxf = ascii_dxf.scale(
            xfact=scale,
            yfact=scale,
            zfact=scale,
            origin=(
                total_bounds[2] - total_bounds[0],
                total_bounds[3] - total_bounds[1]
            )
        )

        # print('total_bounds 2:', total_bounds, file=sys.stderr)

        my_epsg = ascii_dxf.to_crs('EPSG:4326')
        # my_lcc_geojson = ascii_dxf.to_json()

        # total_bounds = my_epsg.total_bounds

        my_epsg = my_epsg.translate(
            xoff=xoff,
            yoff=yoff,
            zoff=0.0
        )

        # my_epsg = my_epsg.rotate(
        #     angle = rot,
        #     origin=(
        #         total_bounds[0],
        #         total_bounds[1]
        #     )
        # )

        # my_epsg = my_epsg.scale(
        #     xfact=scale, yfact=scale, zfact=scale, origin='center'
        # )

        my_geojson = my_epsg.to_json()

        print('geojson_path:', geojson_path, file=sys.stderr)
        logger.info('geojson generated here: %s', geojson_path)
        my_epsg.to_file(geojson_path, driver='GeoJSON')  

        # print("geojson:", my_geojson, file=sys.stderr)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)

    
    # cmd = [
    #     "ogr2ogr", "-f", "GeoJSON",
    #     # "/vsistdin/",
    #     "/vsistdout/",
    #     # geojson_path,
    #     ascii_dxf_path,
    # ]
    # print("cmd:", cmd, file=sys.stderr)

    # my_exec = subprocess.run(
    #     cmd,
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    #     env={
    #         "DXF_ENCODING": "UTF-8",
    #     }
    # )
    # print(my_exec.stdout, file=sys.stderr)
    # print(my_exec.stderr, file=sys.stderr)
    # my_geojson = json.loads(my_exec.stdout)

    return app.response_class(
        response=my_geojson,
        status=200,
        mimetype='application/json'
    )


# wget http://localhost:9090/data/8fa47945beae4b56af301f0b9e0a3dcf.dwg
@app.route('/data/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

# curl http://localhost:9090/api/dwg-to-dxf/8fa47945beae4b56af301f0b9e0a3dcf
@app.route("/api/dwg-to-dxf/<string:file_id>")
def dwg_to_dxf(file_id):
    dest_dir = "/tmp/dwg_" + file_id
    tmp_dwg = dest_dir + "/my.dwg"
    pathlib.Path(dest_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2("/data/" + file_id + ".dwg", tmp_dwg)
# DISPLAY=:99.0 ODAFileConverter \
#     /tmp/dwg_8fa47945beae4b56af301f0b9e0a3dcf \
#     /tmp/dwg_8fa47945beae4b56af301f0b9e0a3dcf \
#     ACAD2018 DXF 1 1 "*.dwg"
    cmd = [
        "ODAFileConverter",
        dest_dir,
        dest_dir,
        "ACAD2018", "DXF", "1", "1", '"*.dwg"'
    ]
    logger.info('cmd: %s', cmd)

    cmd = ["env"]
    subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )

    response = app.response_class(
        status=200,
    )
    return response

if __name__ == '__main__':
    app.run(port=5000, debug=True, host="0.0.0.0")



