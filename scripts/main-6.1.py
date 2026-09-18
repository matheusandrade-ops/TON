import geopandas as gp
import pandas as pd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

RASTER_PATH = "Orthos/Indice_GLI_mask.tif"
OUTPUT_PATH = "Orthos/Indice_GLI_poligonos.geojson"


def polygonize_raster(raster_path: str, output_path: str) -> str:
    """Polygoniza pixels válidos de valor 1, conectados por bordas, em GeoJSON."""
    with rasterio.open(raster_path) as dataset:
        pixels = dataset.read(1)
        eligible = (dataset.read_masks(1) > 0) & (pixels == 1)
        geometries = [
            shape(geometry)
            for geometry, _ in shapes(
                eligible.astype("uint8"), mask=eligible,
                connectivity=4, transform=dataset.transform,
            )
        ]
        result = gp.GeoDataFrame(
            {"DN": pd.Series(1, index=range(len(geometries)), dtype="int32")},
            geometry=geometries, crs=dataset.crs,
        )

    result.to_file(output_path, driver="GeoJSON", index=False)
    print(f"Polígonos gerados: {len(result)}")
    return output_path


def main() -> None:
    output = polygonize_raster(RASTER_PATH, OUTPUT_PATH)
    print(f"Arquivo salvo: {output}")


if __name__ == "__main__":
    main()
