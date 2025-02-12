## OpenHistorical Tiles Coverage

This script identifies areas where roads are located and helps determine the optimal locations for generating tile seeds.


## Execute script

```sh
docker compose -f docker-compose.yaml build
docker compose -f docker-compose.yaml run ohm_tiles_coverage bash

ZOOM=14
python main.py data/transport_lines5-7.shp $ZOOM

```

Make sure you have data/transport_lines5-7.shp  in your local files


## Results:

- https://s3.amazonaws.com/planet.openhistoricalmap.org/tile_coverage/tiles.list
- https://s3.amazonaws.com/planet.openhistoricalmap.org/tile_coverage/tiles.geojson
