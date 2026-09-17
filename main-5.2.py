import geopandas as gp

VECTOR_PATH = "vectors_case_2/plantio_area.geojson"
OUTPUT_PATH = "vectors_case_2/plantio_area_com_area.geojson"


def add_polygon_area(
    gdf: gp.GeoDataFrame, col_name: str = "area_ha"
) -> gp.GeoDataFrame:
    """Retorna uma cópia com área planar em hectares, mantendo o CRS original."""
    crs = gdf.crs.source_crs if gdf.crs.is_bound else gdf.crs
    target_crs = gdf.estimate_utm_crs(datum_name=crs.geodetic_crs.name)
    projected = gdf.to_crs(target_crs)
    result = gdf.copy()
    result[col_name] = projected.geometry.area / 10000
    return result


def main() -> None:
    gdf = gp.read_file(VECTOR_PATH)
    result = add_polygon_area(gdf)
    print("Área por feição (hectares):")
    print(result[["area_ha"]].to_string())
    print(f"\nTotal de feições: {len(result)}")
    print(f"Área total: {result['area_ha'].sum():.6f} ha")
    result.to_file(OUTPUT_PATH, driver="GeoJSON", index=False)
    print(f"Arquivo salvo: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
