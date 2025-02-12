ZOOM=14
python main.py data/transport_lines5-7.shp $ZOOM

aws s3 cp tiles_z$ZOOM/tile_list_z$ZOOM.txt s3://planet.openhistoricalmap.org/tile_coverage/tiles.list --acl public-read

https://s3.amazonaws.com/planet.openhistoricalmap.org/tile_coverage/tiles.list