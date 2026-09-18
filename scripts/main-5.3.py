import geopandas as gp
import pandas as pd

VECTOR_PATH = "vectors_case_2/plantio_area.geojson"
OUTPUT_PATH = "vectors_case_2/plantio_area_poligonos.geojson"


def explode_multipart(gdf: gp.GeoDataFrame) -> gp.GeoDataFrame:
    """Separa multipartes, preservando atributos, CRS e geometrias ausentes/vazias."""
    source = gdf.reset_index(drop=True)
    preserve = source.geometry.isna() | source.geometry.is_empty
    parts = source.loc[~preserve].explode(index_parts=False)
    result = pd.concat([parts, source.loc[preserve]])
    # O índice representa a posição original; a ordenação estável mantém as partes.
    return result.sort_index(kind="stable").reset_index(drop=True)


def main() -> None:
    gdf = gp.read_file(VECTOR_PATH)
    result = explode_multipart(gdf)
    print(f"Feições antes: {len(gdf)}")
    print(f"Feições depois: {len(result)}")
    print(f"Polígonos resultantes: {(result.geom_type == 'Polygon').sum()}")
    print(f"Geometrias ausentes: {result.geometry.isna().sum()}")
    result.to_file(OUTPUT_PATH, driver="GeoJSON", index=False)
    print(f"Arquivo salvo: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
 