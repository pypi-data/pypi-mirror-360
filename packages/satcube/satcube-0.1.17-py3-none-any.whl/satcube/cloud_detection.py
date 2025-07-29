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
import shutil

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
    save_mask: bool = False,
    prefix: str = ""          
) -> pathlib.Path:
    """
    Predict 'image_path' in overlapping patches of 'chunk_size' x 'chunk_size',
    but only write the valid (inner) region to avoid seam artifacts.

    This uses partial overlap logic:
      - For interior tiles, skip overlap//2 on each side.
      - For boundary tiles, we skip only the interior side to avoid losing data at the edges.

    Parameters
    ----------
    image_path : Path to input image.
    output_path : Path to output single-band mask.
    cloud_model : PyTorch model (already loaded with weights).
    chunk_size : Size of each tile to read from the source image (default 512).
    overlap : Overlap in pixels between adjacent tiles (default 32).
    device : "cpu" or "cuda:0".

    Returns
    -------
    pathlib.Path : The path to the created output image.
    """

    input_path = pathlib.Path(input_path)
    output_path = pathlib.Path(output_path)

    with rio.open(input_path) as src:
        meta = src.profile
        if not meta.get("tiled", False):
            raise ValueError("The input image is not marked as tiled in its metadata.")
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
            patch_tensor = torch.from_numpy(patch).float().unsqueeze(0).to(device)
            result = cloud_model(patch_tensor).cpu().numpy().astype(np.uint8)
      
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

    return output_path

def cloud_masking( 
    input: str | pathlib.Path = "raw",
    output: str | pathlib.Path = "masked",
    model_path: str | pathlib.Path = "SEN2CloudEnsemble",
    device: str = "cpu",
    save_mask: bool = False,
    nworks: int = 4,
) -> list[pathlib.Path]:
    """Write cloud-masked Sentinel-2 images.

    Parameters
    ----------
    input
        Path to a single ``.tif`` file **or** a directory containing them.
    output
        Destination directory (created i
        f missing).
    tile, pad
        Tile size and padding (pixels) when tiling is required.
    save_mask
        If *True*, store the binary mask alongside the masked image.
    device
        Torch device for inference, e.g. ``"cpu"`` or ``"cuda:0"``.
    max_pix_cpu
        Tile images larger than this when running on CPU.

    Returns
    ------
    list[pathlib.Path]
        Paths to the generated masked images.
    """
    src = pathlib.Path(input).expanduser().resolve()
    dst_dir = pathlib.Path(output).expanduser().resolve()
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Collect files to process -------------------------------------------------
    tif_paths = []
    if src.is_dir():
        tif_paths = [p for p in src.rglob("*.tif")]
    elif src.is_file() and src.suffix.lower() == ".tif":
        tif_paths = [src]
        src = src.parent  # for relative-path bookkeeping below
    else:
        raise ValueError(f"Input must be a .tif or directory, got: {src}")

    if not tif_paths:
        print(f"[cloud_masking] No .tif files found in {src}")
        return []
    
    if not pathlib.Path(model_path).exists():
        mlstac.download(
            file = "https://huggingface.co/tacofoundation/CloudSEN12-models/resolve/main/SEN2CloudEnsemble/mlm.json",
            output_dir = model_path
        )

    model = mlstac.load(model_path)
    cloud_model = DeviceManager(model, init_device=device).model
    cloud_model.eval()
    
    with ThreadPoolExecutor(max_workers=nworks) as executor:
        futures = { 
            executor.submit(
                infer_cloudmask,
                input_path=p,
                output_path=dst_dir / p.name,
                cloud_model=cloud_model,
                device=device,
                save_mask=save_mask,
                prefix=f"[{i+1}/{len(tif_paths)}] "
            ): p for i, p in enumerate(tif_paths)
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
                print(f"{result} processed successfully.")
            except Exception as e:
                print(f"Error processing {p}: {e}")
                
    metadata = src / "metadata.csv"
    if metadata.exists():
        metadata_dst = dst_dir / "metadata.csv"
        shutil.copy(metadata, metadata_dst)