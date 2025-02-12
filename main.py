import os
import json
import argparse
import geopandas as gpd
import supermercado as sm
import mercantile
import smart_open

parser = argparse.ArgumentParser(description="Generate tiles covering roads and save as GeoJSON.")
parser.add_argument("shapefile_path", type=str, help="Path to the shapefile containing road data")
parser.add_argument("zoom_level", type=int, help="Zoom level for tile generation")
args = parser.parse_args()
shapefile_path = args.shapefile_path
zoom_level = args.zoom_level

# Load shapefile
gdf = gpd.read_file(shapefile_path)
gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]

# Convert to WGS84 (EPSG:4326) if needed
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Generate tile coverage
def generate_tiles(geometry, zoom):
    """Generate tile indices covering road geometries at a specific zoom level using supermercado."""
    tiles = set()
    features = [{"type": "Feature", "geometry": geom.__geo_interface__} for geom in geometry]
    tile_bounds = list(sm.burntiles.burn(features, zoom))
    tiles.update(tuple(tile) for tile in tile_bounds)
    return tiles

# Generate tiles
tiles = generate_tiles(gdf.geometry, zoom_level)

output_dir = f"tiles_z{zoom_level}/"
os.makedirs(output_dir, exist_ok=True)

geojson_tiles = {"type": "FeatureCollection", "features": []}

tile_list_path = os.path.join(output_dir, f"tile_list_z{zoom_level}.txt")
geojson_path = os.path.join(output_dir, f"tiles_z{zoom_level}.geojson")

with open(tile_list_path, "w") as f:
    for tile in tiles:
        tile_bounds = mercantile.bounds(*tile)
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [tile_bounds.west, tile_bounds.south],
                    [tile_bounds.east, tile_bounds.south],
                    [tile_bounds.east, tile_bounds.north],
                    [tile_bounds.west, tile_bounds.north],
                    [tile_bounds.west, tile_bounds.south]
                ]]
            },
            "properties": {"z": int(tile[2]), "x": int(tile[0]), "y": int(tile[1])}
        }
        geojson_tiles["features"].append(feature)
        f.write(f"{tile[2]}/{tile[0]}/{tile[1]}\n")

with open(geojson_path, "w") as f:
    json.dump(geojson_tiles, f, indent=2)

# Upload to AWS S3 using smart_open
s3_tile_list = "s3://planet.openhistoricalmap.org/tile_coverage/tiles.list"
s3_geojson = "s3://planet.openhistoricalmap.org/tile_coverage/tiles.geojson"

print(f"Uploading {tile_list_path} to {s3_tile_list}")
with smart_open.open(s3_tile_list, "w") as s3_file:
    with open(tile_list_path, "r") as local_file:
        s3_file.write(local_file.read())

print(f"Uploading {geojson_path} to {s3_geojson}")
with smart_open.open(s3_geojson, "w") as s3_file:
    with open(geojson_path, "r") as local_file:
        s3_file.write(local_file.read())

print(f"Tile list available at: https://s3.amazonaws.com/planet.openhistoricalmap.org/tile_coverage/tiles.list")
print(f"GeoJSON file available at: https://s3.amazonaws.com/planet.openhistoricalmap.org/tile_coverage/tiles.geojson")
