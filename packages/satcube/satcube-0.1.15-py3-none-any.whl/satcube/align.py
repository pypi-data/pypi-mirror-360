from __future__ import annotations

import pathlib
from typing import List, Tuple
import pickle
import pandas as pd
import satalign
import shutil

import numpy as np
import rasterio as rio
import xarray as xr
from affine import Affine
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def process_row(row: pd.Series, reference: np.ndarray, input_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    row_path = input_dir / (row["id"] + ".tif")
    output_path = output_dir / (row["id"] + ".tif")
    with rio.open(row_path) as src:
        row_image = src.read()
        profile_image = src.profile
    
    row_image_float = row_image.astype(np.float32) / 10000
    row_image_float = row_image_float[np.newaxis, ...]
    
    pcc_model = satalign.LGM(
        datacube     = row_image_float,
        reference    = reference
    )
    image, _ = pcc_model.run_multicore()
    image = (image * 10000).astype(np.uint16).squeeze()

    with rio.open(output_path, "w", **profile_image) as dst:
        dst.write(image)

def align(
    input_dir: str | pathlib.Path = "raw",
    output_dir: str | pathlib.Path = "aligned",
    nworks: int = 4,
    cache: bool = False
) -> None:
    
    input_dir = pathlib.Path(input_dir).expanduser().resolve()
    output_dir = pathlib.Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_path = input_dir / "metadata.csv"
    
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_path}. "
            "Please run the download step first."
        )
    else:
        metadata = pd.read_csv(metadata_path)
        
    if cache:
        exist_files = [file.stem for file in output_dir.glob("*.tif")]
        metadata = metadata[~metadata["id"].isin(exist_files)]
        
        if metadata.empty:
            return

    id_reference = metadata.sort_values(
        by=["cs_cdf", "date"],
        ascending=False,
    ).iloc[0]["id"]
    
    reference_path = input_dir / (id_reference + ".tif")
    
    with rio.open(reference_path) as ref_src:
        reference = ref_src.read()
        
    reference_float = reference.astype(np.float32) / 10000

    with ThreadPoolExecutor(max_workers=nworks) as executor:
        futures = {
            executor.submit(process_row, row, reference_float, input_dir, output_dir)
            for _, row in metadata.iterrows()
        }
        for future in tqdm(
            as_completed(futures), 
            total=len(futures), 
            desc="Aligning images",
            unit="image",
            leave=True
        ):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing image: {e}")
                
    metadata = input_dir / "metadata.csv"
    if metadata.exists():
        metadata_dst = output_dir / "metadata.csv"
        shutil.copy(metadata, metadata_dst)