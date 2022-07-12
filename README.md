# autocad-to-gis
Tool to convert autocad file format to geojson file format

## Build and run

### with docker

```
$ docker build . -t openindoor/autocad-to-gis
$ docker run --rm openindoor/autocad-to-gis
```

### with docker-compose

``` 
docker-compose up autocad-to-gis
```

## Frontend

![Frontend](doc/frontend.png)

## Backend usage

### Specs
```
https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/_LNG_/_LAT_/_XOFFSET_/_YOFFSET_/_ROTATION_/_SCALE_
```

### Example

```
curl -F "file=@data/my_dxf.dxf" \
    https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/3.93/43.56 \
    > my_geojson.geojson
```

Result:

![Latitude/longitude located](doc/lat_lng_location.png)

### Play with OFFSET

```
curl -F "file=@data/my_dxf.dxf" \
    https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/3.93/43.56/0.01/0.0 \
    > my_geojson.geojson
```

![xoffset (longitude)](doc/xoffset.png)

### Play with rotation

```
$ curl -F "file=@data/my_dxf.dxf" \
    https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/3.93/43.56/0.0/0.0/90.0 \
    > my_geojson_90.geojson
```

![rotation](doc/rotation_done.png)

### Play with scaling

```
$ curl -F "file=@data/my_dxf.dxf" \
    https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/3.93/43.56/0.0/0.0/0.0/0.5 \
    > my_geojson_0_5.geojson
```

![rotation](doc/scale.png)

### Setup

```
$ curl \
    -F "file=@data/my_dxf.dxf" \
    -F "setup=@data/setup.json" \
    https://autocad-to-geojson.openindoor.io/api/autocad-to-gis/convert/3.93/43.56/0.0/0.0/0.0/0.5 \
    > my_geojson_0_5.geojson
```

## Maintainer

![OpenIndoor](https://www.openindoor.net)