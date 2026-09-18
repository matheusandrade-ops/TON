import geopandas
import pandas as pd

VECTOR_PATH = "vectors_case_1/MATOLOGIA_Orthomosaico.geojson"


def load_vector(path: str) -> geopandas.GeoDataFrame:
    """Lê e inspeciona um vetor, retornando os dados sem modificações."""
    gdf = geopandas.read_file(path)
    print(f"Elementos: {len(gdf)}")

    kind = (
        "geográfico" if gdf.crs.is_geographic
        else "projetado" if gdf.crs.is_projected
        else "outro"
    )

    print(f"CRS: {gdf.crs} ({kind})")
    print("\nTipos de geometria:")
    print(gdf.geom_type.value_counts().to_string())
    print("\nColunas:")
    print(pd.DataFrame({
        "tipo": gdf.dtypes.astype(str),
        "ausentes": gdf.isna().sum(),
    }).to_string())

    return gdf


def main() -> None:
    load_vector(VECTOR_PATH)


if __name__ == "__main__":
    main()
