import geopandas

VECTOR_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico.geojson"
OUTPUT_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico_filtrado.geojson"


def filter_by_attribute(
    gdf: geopandas.GeoDataFrame, expression: str | None
) -> geopandas.GeoDataFrame:
    """Filtra com query (ex.: 'DN == 1'), analisa DN e retorna as feições."""
    if expression is not None:
        gdf = gdf.query(expression)

    dn = gdf["DN"]
    unique_values = dn.dropna().drop_duplicates().sort_values().tolist()
    counts = dn.value_counts(dropna=False).sort_index(na_position="last")
    distribution = counts.rename_axis("Classe DN").reset_index(name="Quantidade de geometrias")

    print(f"Tipo do atributo DN: {dn.dtype}")
    print(f"Valores únicos: {unique_values}")
    print(f"Total de classes: {len(unique_values)}")
    print(f"Total de geometrias: {len(gdf)}")
    print("\nDistribuição por classe:")
    print(distribution.to_string(index=False))
    return gdf


def main() -> None:
    gdf = geopandas.read_file(VECTOR_PATH)
    filtered_gdf = filter_by_attribute(gdf, expression="DN == 3")
    filtered_gdf.to_file(OUTPUT_PATH, driver="GeoJSON", index=False)
    print(f"\nArquivo salvo: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
