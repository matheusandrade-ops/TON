import geopandas as gp

VECTOR_PATH = "vectors_case_2/LINHAS.geojson"
OUTPUT_PATH = "vectors_case_2/LINHAS_com_comprimento.geojson"


def add_linestring_length(gdf: gp.GeoDataFrame, col_name: str = "length_m") -> gp.GeoDataFrame:
    """Adiciona o comprimento em metros a uma cópia, mantendo o CRS original."""
    crs = gdf.crs.source_crs if gdf.crs.is_bound else gdf.crs
    target_crs = gdf.estimate_utm_crs(datum_name=crs.geodetic_crs.name)
    result = gdf.copy()
    result[col_name] = gdf.to_crs(target_crs).length
    return result


def main() -> None:
    gdf = gp.read_file(VECTOR_PATH)
    result = add_linestring_length(gdf)
    print("Comprimento por feição (metros):")
    print(result[["length_m"]].to_string())
    print(f"\nTotal de geometrias: {len(result)}")
    print(f"Comprimento total: {result['length_m'].sum():.3f} m")
    result.to_file(OUTPUT_PATH, driver="GeoJSON", index=False)
    print(f"Arquivo salvo: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
