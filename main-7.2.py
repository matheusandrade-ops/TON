from pathlib import Path
import geopandas as gp
import pandas as pd

VECTOR_PATH = Path("vectors_case_2/plantio_area.geojson")
GRID_PATH = Path("vectors_case_2/grid.geojson")


def tile_by_grid(gdf: gp.GeoDataFrame, grid: gp.GeoDataFrame) -> gp.GeoDataFrame:
    """Recorta os polígonos por célula e identifica sua posição em cell_index."""

    source = gdf.to_crs(grid.crs) if gdf.crs != grid.crs else gdf.copy()
    tiles = []
    for cell_index, cell in enumerate(grid.geometry):
        clipped = gp.clip(source, cell, keep_geom_type=True)
        clipped = clipped.loc[~clipped.geometry.is_empty].copy()
        # Após o recorte, contatos que são apenas linhas ou pontos não têm área.
        clipped = clipped.loc[clipped.geometry.apply(lambda geometry: geometry.area > 0)].copy()
        if not clipped.empty:
            clipped["cell_index"] = cell_index
            tiles.append(clipped)

    if not tiles:
        result = source.iloc[:0].copy()
        result["cell_index"] = pd.Series(dtype="int64")
        return result.reset_index(drop=True)
    return gp.GeoDataFrame(
        pd.concat(tiles, ignore_index=True), geometry=source.geometry.name, crs=grid.crs
    )


def main() -> None:
    gdf = gp.read_file(VECTOR_PATH)
    grid = gp.read_file(GRID_PATH)
    tiles = tile_by_grid(gdf, grid)
    output_dir = VECTOR_PATH.parent / VECTOR_PATH.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    for cell_index in range(len(grid)):
        tile = tiles.loc[tiles["cell_index"] == cell_index]
        output_path = output_dir / f"{VECTOR_PATH.stem}_{cell_index}.geojson"
        tile.to_file(output_path, driver="GeoJSON", index=False, mode="w")
    print(f"{len(grid)} arquivos salvos em {output_dir}")


if __name__ == "__main__":
    main()
