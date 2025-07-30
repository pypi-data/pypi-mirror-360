"""Predict cloud masks for Sentinel-2 GeoTIFFs with the SEN2CloudEnsemble model.

The callable :pyfunc:`cloud_masking` accepts **either** a single ``.tif`` file  
or a directory tree; in both cases it writes a masked copy of every image (and,
optionally, the binary mask) to *output*.

Example
-------
>>> from satcube.cloud_detection import cloud_masking
>>> cloud_masking("~/s2/input", "~/s2/output", device="cuda")
"""

from __future__ import annotations

import pathlib

import mlstac
import numpy as np
import rasterio as rio
from rasterio.windows import Window
import torch
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import rasterio as rio
from rasterio.merge import merge
from satcube.utils import define_iteration, DeviceManager
import warnings
warnings.filterwarnings(
    "ignore",
    message="The secret HF_TOKEN does not exist in your Colab secrets.",
    category=UserWarning,
    module=r"huggingface_hub\.utils\._.*",
)

def infer_cloudmask(
    input_path: str | pathlib.Path,
    output_path: str | pathlib.Path,
    cloud_model: torch.nn.Module,
    *,
    chunk_size: int = 512,
    overlap: int = 32,
    device: str = "cpu",
    save_mask: bool = True      
) -> pathlib.Path:
 
    input_path = pathlib.Path(input_path).expanduser().resolve()
    output_path = pathlib.Path(output_path).expanduser().resolve()

    with rio.open(input_path) as src:
        meta = src.profile
        # if not meta.get("tiled", False):
        #     raise ValueError("The input image is not marked as tiled in its metadata.")
        # Ensure the internal blocksize matches chunk_size
        if chunk_size % meta["blockxsize"] != 0 and meta["blockxsize"] <= chunk_size:
            raise ValueError(f"Image blocks must be {chunk_size}x{chunk_size}, "
                            f"got {meta['blockxsize']}x{meta['blockysize']}")
        height, width = meta["height"], meta["width"]

    full_mask = np.zeros((height, width), dtype=np.float32)

    coords = define_iteration((height, width), chunk_size, overlap)

    with rio.open(input_path) as src:

        for (row_off, col_off) in coords: 

            window = Window(col_off, row_off, chunk_size, chunk_size)
            patch = src.read(window=window) / 1e4
            
            patch_tensor = (
                torch.from_numpy(patch)
                .float()
                .unsqueeze(0)
                .to(device)
            )
            
            result = (
                cloud_model(patch_tensor)
                .cpu()
                .numpy()
                .astype(np.uint8)
            )

            if col_off == 0:
                offset_x = 0
            else:
                offset_x = col_off + overlap // 2
            if row_off == 0:
                offset_y = 0
            else:
                offset_y = row_off + overlap // 2
            if (offset_x + chunk_size) == width:
                length_x = chunk_size
                sub_x_start = 0
            else:
                length_x = chunk_size - (overlap // 2)
                sub_x_start = overlap // 2 if col_off != 0 else 0

            if (offset_y + chunk_size) == height:
                length_y = chunk_size
                sub_y_start = 0
            else:
                length_y = chunk_size - (overlap // 2)
                sub_y_start = overlap // 2 if row_off != 0 else 0

            full_mask[
                offset_y : offset_y + length_y,
                offset_x : offset_x + length_x
            ] = result[
                sub_y_start : sub_y_start + length_y,
                sub_x_start : sub_x_start + length_x
            ]

        if save_mask:
            out_meta = meta.copy()
            out_meta.update(count=1, dtype="uint8", nodata=255)
            output_mask = output_path.parent / (output_path.stem + "_mask.tif")
            with rio.open(output_mask, "w", **out_meta) as dst:
                dst.write(full_mask, 1)
                
        data = src.read()
        img_prof = src.profile.copy()

        masked = data.copy()
        masked[:, full_mask != 0] = 65535
        img_prof.update(dtype="uint16", nodata=65535)

        with rio.open(output_path, "w", **img_prof) as dst:
            dst.write(masked)

    flat = full_mask.astype(np.uint8).ravel()
    counts = np.bincount(flat, minlength=4)
    total  = flat.size
    percentages = {
        "id": input_path.stem,
        "clear_pct":         counts[0] / total * 100.0,
        "thin_cloud_pct":    counts[1] / total * 100.0,
        "cloud_shadow_pct":  counts[2] / total * 100.0,
        "thick_cloud_pct":   counts[3] / total * 100.0,
    }

    return percentages


def cloud_fn( 
    metadata: pd.DataFrame | None = None,   
    input_dir: str | pathlib.Path | None = None,
    output_dir: str | pathlib.Path = "masked",
    model_path: str | pathlib.Path = "SEN2CloudEnsemble",
    device: str = "cpu",
    save_mask: bool = True,
    cache: bool = False,
    nworks: int = 4,
) -> pd.DataFrame | None:
    
    input_dir = pathlib.Path(input_dir).expanduser().resolve()
    output_dir = pathlib.Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if metadata is None:
        if not input_dir:
            raise ValueError("Input directory must be specified.")
        else:
            if input_dir.is_dir():
                tif_paths = [p for p in input_dir.rglob("*.tif")]
                df = pd.DataFrame({
                    "id": [p.stem for p in tif_paths],
                    "path": [str(p) for p in tif_paths]
                })
            elif input_dir.is_file() and input_dir.suffix.lower() == ".tif":
                tif_paths = [input_dir]
                input_dir = input_dir.parent
            else:
                raise ValueError(f"Input must be a .tif or directory, got: {input_dir}")
    else:
        if not input_dir:
            raise ValueError("Input directory must be specified.")
        else:
            df = metadata["id"].to_frame()
            df["path"] = df["id"].apply(lambda x: str(input_dir / (x + ".tif")))
        
        
    if cache:
        exist_files = [file.stem for file in output_dir.glob("*.tif")]
        df = df[~df["id"].isin(exist_files)]
        
    if not pathlib.Path(model_path).exists():
        mlstac.download(
            file = "https://huggingface.co/tacofoundation/CloudSEN12-models/resolve/main/SEN2CloudEnsemble/mlm.json",
            output_dir = model_path
        )

    model = mlstac.load(model_path)
    cloud_model = DeviceManager(model, init_device=device).model.eval()

    results_cloud = []
    
    with ThreadPoolExecutor(max_workers=nworks) as executor:
        futures = { 
            executor.submit(
                infer_cloudmask,
                input_path=p["path"],
                output_path=output_dir / (p["id"] + ".tif"),
                cloud_model=cloud_model,
                device=device,
                save_mask=save_mask
            ): p for i, p in df.iterrows()
        }
        
        
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Cloud Masking",
            position=0,
            leave=True
        ):
            p = futures[future]
            try:
                result = future.result()
                results_cloud.append(result)
            except Exception as e:
                print(f"Error processing {p}: {e}")
                
    cloud_df = pd.DataFrame(results_cloud)
    
    if cloud_df.empty:
        return metadata
    
    metadata = metadata.drop(
        columns=["clear_pct","thin_cloud_pct", "cloud_shadow_pct", "thick_cloud_pct"], 
        errors="ignore"
    )
    
    metadata = metadata.merge(
        cloud_df,
        on="id",
        how="left",
        suffixes=('', '') 
    )
    
    return metadata