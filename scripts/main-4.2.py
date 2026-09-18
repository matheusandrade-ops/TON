from math import floor
import geopandas
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely import get_coordinates

VECTOR_PATH = "vectors_case_1/shape.geojson"


def _geodetic_crs(gdf: geopandas.GeoDataFrame) -> CRS:
    crs = gdf.crs.source_crs if gdf.crs.is_bound else gdf.crs
    return crs.geodetic_crs


def identify_utm_crs(gdf: geopandas.GeoDataFrame) -> int:
    """Retorna o menor EPSG UTM compatível com o centro da área e o datum."""
    geodetic = _geodetic_crs(gdf)
    geographic = gdf.to_crs(4326)
    min_lon, min_lat, max_lon, max_lat = geographic.total_bounds
    longitude = (min_lon + max_lon) / 2
    latitude = (min_lat + max_lat) / 2

    # Ajusta áreas que cruzam ±180°.
    if max_lon - min_lon > 180:
        longitudes = get_coordinates(geographic.geometry.array)[:, 0] % 360
        longitude = (longitudes.min() + longitudes.max()) / 2
        longitude = (longitude + 180) % 360 - 180

    longitude = round(float(longitude), 10)
    latitude = round(float(latitude), 10)
    zone = max(1, min(60, floor((longitude + 180) / 6) + 1))
    utm_zone = f"{zone}{'N' if latitude >= 0 else 'S'}"

    # Busca o EPSG da região que mantém o datum e o fuso calculado.
    candidates = query_utm_crs_info(
        area_of_interest=AreaOfInterest(longitude, latitude, longitude, latitude)
    )
    matches = (CRS.from_epsg(info.code) for info in candidates)
    return min(
        candidate.to_epsg() for candidate in matches
        if candidate.utm_zone == utm_zone and candidate.datum == geodetic.datum
    )


def main() -> None:
    gdf = geopandas.read_file(VECTOR_PATH)
    own_crs = CRS(identify_utm_crs(gdf))
    estimated_crs = gdf.estimate_utm_crs(datum_name=_geodetic_crs(gdf).name)
    print(f"Estimativa própria: {own_crs.name} (EPSG:{own_crs.to_epsg()})")
    print(f"GeoPandas: {estimated_crs.name} (EPSG:{estimated_crs.to_epsg()})")


if __name__ == "__main__":
    main()
