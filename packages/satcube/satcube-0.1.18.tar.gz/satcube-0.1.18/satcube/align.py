from __future__ import annotations

import pathlib
from typing import Tuple
import pandas as pd
import satalign
import numpy as np
import rasterio as rio
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def _process_image(
    image: np.ndarray, 
    reference: np.ndarray, 
    profile: dict,
    output_path: pathlib.Path,
) -> Tuple[float, float]:
    
    image_float = image.astype(np.float32) / 10000
    image_float = image_float[np.newaxis, ...]
    
    image, M = satalign.LGM(
        datacube=image_float,
        reference=reference
    ).run_multicore()
    
    image = (image * 10000).astype(np.uint16).squeeze()

    with rio.open(output_path, "w", **profile) as dst:
        dst.write(image)
    
    return M[0][0, 2], M[0][1, 2]

def _process_row(
    row: pd.Series, 
    reference: np.ndarray, 
    input_dir: pathlib.Path, 
    output_dir: pathlib.Path
) -> Tuple[str, float, float]:
    
    row_path = input_dir / (row["id"] + ".tif")
    output_path = output_dir / (row["id"] + ".tif")
    
    with rio.open(row_path) as src:
        image = src.read()
        profile = src.profile
    
    dx_px, dy_px = _process_image(
        image=image,
        reference=reference,
        profile=profile,
        output_path=output_path
    )
    
    return row["id"], dx_px, dy_px 

def align_fn(
    metadata: pd.DataFrame | None = None,
    input_dir: str | pathlib.Path = "raw",
    output_dir: str | pathlib.Path = "aligned",
    nworks: int = 4,
    cache: bool = False
) -> pd.DataFrame | None:
    
    input_dir = pathlib.Path(input_dir).expanduser().resolve()
    output_dir = pathlib.Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
        
    if metadata is None:
        raise FileNotFoundError(
            f"Add metadata file to do alignment."
            "Please run the download step first."
        )
        

    id_reference = metadata.sort_values(
        by=["cs_cdf"],
        ascending=False,
    ).iloc[0]["id"]
    
    df = metadata.copy()
    
    if cache:
        exist_files = [file.stem for file in output_dir.glob("*.tif")]
        df = df[~df["id"].isin(exist_files)]
        if df.empty:
            return metadata
        
    reference_path = input_dir / (id_reference + ".tif")
    
    with rio.open(reference_path) as ref_src:
        reference = ref_src.read()
        
    reference_float = reference.astype(np.float32) / 10000

    results = []
    
    with ThreadPoolExecutor(max_workers=nworks) as executor:
        futures = {
            executor.submit(
                _process_row, 
                row=row, 
                reference=reference_float, 
                input_dir=input_dir, 
                output_dir=output_dir
            ): row["id"]
            for _, row in df.iterrows()
        }
        
        for future in tqdm(
            as_completed(futures), 
            total=len(futures), 
            desc="Aligning images",
            unit="image",
            leave=True
        ):
            try:
                img_id, dx_px, dy_px = future.result()
                results.append({"id": img_id,
                                "dx_px": dx_px,
                                "dy_px": dy_px})
            except Exception as e:
                print(f"Error processing image: {e} {futures[future]}")
    
    shift_df = pd.DataFrame(results)
    
    metadata = metadata.drop(
        columns=["dx_px","dy_px"], 
        errors="ignore"
    )
    
    metadata = metadata.merge(
        shift_df,
        on="id",
        how="left",
        suffixes=('', '') 
    )
    
    return metadata