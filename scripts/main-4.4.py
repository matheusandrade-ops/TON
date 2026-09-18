import geopandas

VECTOR_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico.geojson"
OUTPUT_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico_reprojetado.geojson"


def reproject_gdf(
    gdf: geopandas.GeoDataFrame, target_epsg: int
) -> geopandas.GeoDataFrame:
    """Reprojeta as feições para o EPSG informado."""
    return gdf.to_crs(epsg=target_epsg)


def main() -> None:
    gdf = geopandas.read_file(VECTOR_PATH)
    crs = gdf.crs.source_crs if gdf.crs.is_bound else gdf.crs
    target_epsg = gdf.estimate_utm_crs(datum_name=crs.geodetic_crs.name).to_epsg()
    projected = reproject_gdf(gdf, target_epsg)

    print(f"CRS de origem: {gdf.crs}")
    print(f"CRS de destino: {projected.crs.name} (EPSG:{target_epsg})")
    print(f"Total de geometrias: {len(projected)}")
    projected.to_file(OUTPUT_PATH, driver="GeoJSON", index=False)
    print(f"Arquivo salvo: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
