# satcube/gapfill.py
from __future__ import annotations

import pathlib, shutil
from typing import Literal, List, Tuple
import numpy as np
import pandas as pd
import rasterio as rio
from tqdm import tqdm

from sklearn.linear_model import LinearRegression

_GAP_METHOD = Literal["histogram_matching", "linear"]




def linear_interpolation(
    image1: np.ndarray, image2: np.ndarray, image3: np.ndarray
) -> np.ndarray:
    """Apply linear interpolation to image3 using image1 and image2 as
    reference images.

    Args:
        image1 (np.ndarray): The first reference image.
        image2 (np.ndarray): The second reference image.
        image3 (np.ndarray): The image to be matched.

    Returns:
        np.ndarray: The matched image.
    """

    # remove nan values
    image1_nonan = image1.flatten().copy()
    image1_nonan = image1_nonan[~np.isnan(image1_nonan)]

    image2_nonan = image2.flatten().copy()
    image2_nonan = image2_nonan[~np.isnan(image2_nonan)]

    # Calculate the slope and intercept
    linreg = LinearRegression()
    linreg.fit(image2_nonan[:, np.newaxis], image1_nonan[:, np.newaxis])
    slope = linreg.coef_[0]
    intercept = linreg.intercept_

    # Apply the linear interpolation
    image3_matched = slope * image3 + intercept

    return image3_matched


def tripple_histogram_matching(
    image1: np.ndarray, image2: np.ndarray, image3: np.ndarray
) -> np.ndarray:
    """Apply histogram matching to image3 using image1 and image2 as reference images.

    Args:
        image1 (np.ndarray): The first reference image.
        image2 (np.ndarray): The second reference image.
        image3 (np.ndarray): The image to be matched.

    Returns:
        np.ndarray: The matched image.
    """

    # remove nan values
    image1_nonan = image1.flatten().copy()
    image1_nonan = image1_nonan[~np.isnan(image1_nonan)]

    image2_nonan = image2.flatten().copy()
    image2_nonan = image2_nonan[~np.isnan(image2_nonan)]

    image3_nonan = image3.flatten().copy()
    image3_nonan = image3_nonan[~np.isnan(image3_nonan)]

    # Calculate histograms
    hist1, bins = np.histogram(image1_nonan, 128, [0, 2])
    hist2, bins = np.histogram(image2_nonan, 128, [0, 2])
    hist3, bins = np.histogram(image3_nonan, 128, [0, 2])

    # Calculate the cumulative distribution function (CDF) of img1
    cdf1 = hist1.cumsum() / hist1.sum()

    # Calculate the CDF of img2
    cdf2 = hist2.cumsum() / hist2.sum()

    # Create a lookup table (LUT) to map the pixel values of img1 to img2
    lut = np.interp(cdf2, cdf1, bins[:-1])

    # Perform histogram matching
    img3_matched = np.interp(image3.ravel(), bins[:-1], lut).reshape(image3.shape)

    return img3_matched


def _fill_one(
    img_path: pathlib.Path,
    ref_paths: List[pathlib.Path],
    dates: np.ndarray,
    this_date: np.datetime64,
    *,
    method: _GAP_METHOD,
    out_dir: pathlib.Path,
    quiet: bool
) -> float:
    """Gap‑fill a single S2 scene; return error metric."""
    with rio.open(img_path) as src:
        data = src.read() / 1e4
        prof = src.profile
        data[data == 6.5535] = np.nan
        cloudmask = np.isnan(data).mean(0)

    if cloudmask.sum() == 0:              # imagen limpia: copia sin procesar
        shutil.copy(img_path, out_dir / img_path.name)
        return 0.0

    # ordenar todas las demás por cercanía temporal
    idxs = np.argsort(np.abs(dates - this_date))
    best_img, best_metric = None, np.inf
    tries = 0

    for i in idxs:
        if tries == 5:                    # máximo 5 intentos
            break
        ref_path = ref_paths[i]
        if ref_path == img_path:
            continue

        with rio.open(ref_path) as src:
            ref = src.read() / 1e4
            ref[ref == 6.5535] = np.nan
            ref_mask = np.isnan(ref) * 1.0

        # descartar ref con nubes superpuestas
        if np.sum((ref_mask + cloudmask) == 2) != 0:
            continue

        full_mask = ((cloudmask + ref_mask) > 0).astype(float)
        data_masked = np.where(full_mask, np.nan, data)
        ref_masked  = np.where(full_mask, np.nan, ref)

        filled = np.zeros_like(data)
        for b in range(data.shape[0]):
            if method == "histogram_matching":
                filled[b] = tripple_histogram_matching(data_masked[b], ref_masked[b], ref[b])
            else:                         # "linear"
                filled[b] = linear_interpolation(data_masked[b], ref_masked[b], ref[b])

        # calcular métrica
        a = filled[[2, 1, 0]].mean(0)
        b = data[[2, 1, 0]].mean(0)
        metric = np.nanmean(np.abs(a - b) / (a + b))

        if metric < best_metric:
            best_metric = metric
            best_img    = filled

        tries += 1

    if best_img is None:                 # no suitable ref found
        if not quiet:
            print(f"{img_path.name}: no cloud‑free neighbour found – copied.")
        shutil.copy(img_path, out_dir / img_path.name)
        return np.nan                    # could also return 0.0

    # Ensure float dtype for isnan()
    if best_img.dtype.kind in "iu":      # i = int, u = uint
        best_img = best_img.astype(np.float32)

    # Combine and save
    best_img[np.isnan(best_img)] = 0
    data[np.isnan(data)]         = 0
    final = data + best_img * full_mask
    final[final < 0] = 0
    final = (final * 1e4).astype(np.uint16)

    with rio.open(out_dir / img_path.name, "w", **prof) as dst:
        dst.write(final)

    if not quiet:
        print(f"{img_path.name} gap‑filled (error={best_metric:.4f})")

    return float(best_metric)


def gapfill_fn(                                   # ← wrapper estilo align_fn
    metadata: pd.DataFrame,
    input_dir: str | pathlib.Path,
    output_dir: str | pathlib.Path = "gapfilled",
    *,
    method: _GAP_METHOD = "histogram_matching",
    quiet: bool = False
) -> pd.DataFrame:
    """Gap‑fill every image listed in *metadata*.

    Returns
    -------
    pd.DataFrame
        Original dataframe + column ``match_error``.
    """
    input_dir  = pathlib.Path(input_dir).expanduser().resolve()
    output_dir = pathlib.Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    img_paths  = [input_dir / f"{i}.tif" for i in metadata["id"]]
    dates      = pd.to_datetime(metadata["date"]).to_numpy()

    errors: List[float] = []
    for i, img in enumerate(tqdm(img_paths, desc="Gap‑filling", unit="img")):
        err = _fill_one(img, img_paths, dates, dates[i],
                        method=method, out_dir=output_dir, quiet=quiet)
        errors.append(err)

    metadata = metadata.drop(columns=["match_error"], errors="ignore")
    metadata["match_error"] = errors
    return metadata
