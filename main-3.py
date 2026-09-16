from pathlib import Path

import rasterio
import numpy as np

#RASTER_PATH = "Orthos/Orthomosaico.tif"
RASTER_PATH = "Orthos/Indice_GLI.tif"
#RASTER_PATH = "Orthos/MDS.tif"

def raster_band_stats(raster_path: str | Path) -> dict[int, dict[str, dict[str, float]]]:
    """Compara estatísticas por banda via Rasterio/GDAL e NumPy com máscara.

    NumPy ignora os pixels mascarados; Rasterio usa o tratamento do GDAL.
    As estatísticas podem ser gravadas pelo GDAL nos metadados ou em .aux.xml.
    """
    with rasterio.open(raster_path) as dataset:
        bands = {}
        for band, stats in zip(dataset.indexes, dataset.stats(approx=False)):
            rasterio_stats = {
                "min": stats.min,
                "max": stats.max,
                "mean": stats.mean,
                "std": stats.std,
            }
            pixels = dataset.read(band, masked=True)
            numpy_stats = {
                "min": pixels.min(),
                "max": pixels.max(),
                "mean": pixels.mean(dtype=np.float64),
                "std": pixels.std(dtype=np.float64, ddof=0),
            }
            bands[band] = {
                "rasterio": rasterio_stats,
                "numpy": numpy_stats,
                "difference": {
                    key: abs(rasterio_stats[key] - numpy_stats[key])
                    for key in rasterio_stats
                },
            }
        return bands


def main() -> None:
    bands = raster_band_stats(RASTER_PATH)
    for band, stats in bands.items():
        print(f"\nBanda {band} — diferença absoluta entre os métodos:")
        print(f"{'Estatística':<16} {'Rasterio':>18} {'NumPy (máscara)':>18} {'Diferença':>14}")
        for key, label in (
            ("min", "Mínimo"), ("max", "Máximo"),
            ("mean", "Média"), ("std", "Desvio padrão"),
        ):
            print(f"{label:<16} {stats['rasterio'][key]:>18.10f} {stats['numpy'][key]:>18.10f} {stats['difference'][key]:>14.6g}")


if __name__ == "__main__":
    main()
