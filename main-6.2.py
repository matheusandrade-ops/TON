from math import ceil
from pathlib import Path

import geopandas as gp
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin

VECTOR_PATH = "Orthos/Indice_GLI_poligonos.geojson"
OUTPUT_PATH = "Orthos/Indice_GLI_rasterizado.tif"
RESOLUTION = 0.10  # Metros por pixel.
VALUE_COLUMN = "DN"
FILL_VALUE = 0


def rasterize_vector(vector_path: str | Path, output_path: str | Path) -> Path:
    """Rasteriza polígonos pelo centro dos pixels, usando os valores de DN."""
    gdf = gp.read_file(vector_path)
    usable = ~gdf.geometry.isna() & ~gdf.geometry.is_empty
    gdf = gdf.loc[usable]
    if gdf.crs.is_geographic:
        crs = gdf.crs.source_crs if gdf.crs.is_bound else gdf.crs
        target_crs = gdf.estimate_utm_crs(datum_name=crs.geodetic_crs.name)
        gdf = gdf.to_crs(target_crs)

    min_x, min_y, max_x, max_y = gdf.total_bounds
    width = ceil((max_x - min_x) / RESOLUTION)
    height = ceil((max_y - min_y) / RESOLUTION)
    transform = from_origin(min_x, max_y, RESOLUTION, RESOLUTION)
    pixels = rasterize(
        zip(gdf.geometry, gdf[VALUE_COLUMN]),
        out_shape=(height, width), transform=transform,
        fill=FILL_VALUE, dtype="int32", all_touched=False,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path, "w", driver="GTiff", width=width, height=height,
        count=1, dtype="int32", crs=gdf.crs, transform=transform, nodata=None,
    ) as output:
        output.write(pixels, 1)
    return output_path


def main() -> None:
    output = rasterize_vector(VECTOR_PATH, OUTPUT_PATH)
    with rasterio.open(output) as dataset:
        print(f"Arquivo salvo: {output}")
        print(f"CRS: {dataset.crs}")
        print(f"Resolução: {dataset.res[0]} × {dataset.res[1]} m")
        print(f"Dimensões: {dataset.width} × {dataset.height} pixels")
        print(f"Valores únicos: {np.unique(dataset.read(1)).tolist()}")


if __name__ == "__main__":
    main()
