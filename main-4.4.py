import geopandas
from pyproj import CRS


VECTOR_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico.geojson"
OUTPUT_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico_reprojetado.geojson"


def _geodetic_crs(gdf: geopandas.GeoDataFrame) -> CRS:
    crs = gdf.crs.source_crs if gdf.crs.is_bound else gdf.crs
    return crs.geodetic_crs


def reproject_gdf(
    gdf: geopandas.GeoDataFrame, target_epsg: int
) -> geopandas.GeoDataFrame:
    """Retorna as feições reprojetadas, sem alterar o GeoDataFrame original."""
    return gdf.to_crs(epsg=target_epsg)


def main() -> None:
    gdf = geopandas.read_file(VECTOR_PATH)
    target_crs = gdf.estimate_utm_crs(datum_name=_geodetic_crs(gdf).name)
    target_epsg = target_crs.to_epsg()
    projected = reproject_gdf(gdf, target_epsg)

    print(f"CRS de origem: {gdf.crs}")
    print(f"CRS de destino: {projected.crs.name} (EPSG:{target_epsg})")
    print(f"Total de geometrias: {len(projected)}")
    projected.to_file(
        OUTPUT_PATH, driver="GeoJSON", index=False, mode="w"
    )
    print(f"Arquivo salvo: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
