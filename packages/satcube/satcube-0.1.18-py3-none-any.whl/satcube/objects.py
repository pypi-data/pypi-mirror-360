from __future__ import annotations
from dataclasses import dataclass, field
import pathlib
import pandas as pd
from typing import Tuple
from datetime import datetime
import numpy as np
import xarray as xr
import rasterio as rio
import torch

from satcube.align  import align_fn
from satcube.cloud  import cloud_fn
from satcube.gapfill import gapfill_fn 
from satcube.composite import monthly_composites_s2
from satcube.smooth import gaussian_smooth

@dataclass
class SatCubeMetadata:
    df: pd.DataFrame
    raw_dir: pathlib.Path
    _current_dir: pathlib.Path | None = None


    def _dir(self) -> pathlib.Path:
        return self._current_dir or self.raw_dir
    
    def _spawn(self, *, df: pd.DataFrame, current_dir: pathlib.Path) -> "SatCubeMetadata":
        return SatCubeMetadata(df=df, raw_dir=self.raw_dir, _current_dir=current_dir)
        
    def align(
        self,
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "aligned",
        nworks: int = 4,
        cache: bool = False
    ) -> "SatCubeMetadata":

        self.aligned_dir = pathlib.Path(output_dir).resolve()
        
        input_dir = pathlib.Path(input_dir).expanduser().resolve() if input_dir else self._dir()
        output_dir = pathlib.Path(output_dir).resolve()
        
        new_df = align_fn(
            metadata=self.df,
            input_dir=input_dir, 
            output_dir=self.aligned_dir, 
            nworks=nworks, 
            cache=cache
        )
                
        return self._spawn(df=new_df, current_dir=output_dir)

    def cloud_masking(
        self,
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "masked",
        device: str = "cpu",
        cache: bool = False,
        nworks: int = 4,
    ) -> "SatCubeMetadata":
        
        input_dir = pathlib.Path(input_dir).expanduser().resolve() if input_dir else self._dir()
        output_dir = pathlib.Path(output_dir).resolve()

            
        new_df = cloud_fn(
            metadata=self.df,
            input_dir=input_dir,
            output_dir=output_dir,
            device=device,
            nworks=nworks,
            cache=cache
        )
        
        return self._spawn(df=new_df, current_dir=output_dir)

    def gap_fill(
        self,
        *,
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "gapfilled",
        method: str = "histogram_matching",
        quiet: bool = False
    ) -> "SatCubeMetadata":
        """Fill small cloud/shadow gaps on top of current stack."""
        in_dir  = pathlib.Path(input_dir).expanduser().resolve() if input_dir else self._dir()
        out_dir = pathlib.Path(output_dir).resolve()

        new_df = gapfill_fn(
            metadata=self.df,
            input_dir=in_dir,
            output_dir=out_dir,
            method=method,
            quiet=quiet,
        )
        
        return self._spawn(df=new_df, current_dir=out_dir)
    
    def monthly_composites(
        self,
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "monthly_composites",
        agg_method: str = "median"
    ) -> "SatCubeMetadata":
        
        input_dir = pathlib.Path(input_dir).expanduser().resolve() if input_dir else self._dir()
        output_dir = pathlib.Path(output_dir).resolve()
        
        date_range = (self.df["date"].min(), self.df["date"].max())

        out_table = monthly_composites_s2(
            metadata=self.df,
            input_dir=input_dir,
            output_dir=output_dir,
            date_range=date_range,
            agg_method=agg_method
        )

        return self._spawn(df=out_table, current_dir=output_dir)
    
    def interpolate(
        self, 
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "interpolated",
    ) -> "SatCubeMetadata":


        input_dir = pathlib.Path(input_dir).expanduser().resolve() if input_dir else self._dir()
        output_dir = pathlib.Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        all_raw_files = [input_dir / f for f in input_dir.glob("*.tif") if f.is_file()]

        all_raw_files.sort()
        all_raw_dates = pd.to_datetime(self.df["date"])

        # Create a data cube with xarray
        profile = rio.open(all_raw_files[0]).profile
        data_np = np.array([rio.open(file).read() for file in all_raw_files]) / 10000  # Normalize
        data_np[data_np == 6.5535] = np.nan  # Set NoData values to NaN
        data_np = xr.DataArray(
            data=data_np,
            dims=("time", "band", "y", "x"),
            coords={"time": all_raw_dates, "band": range(13)},
        )

        data_np = data_np.interpolate_na(dim="time", method="linear")

        # Save the interpolated images
        for idx, file in enumerate(all_raw_files):
            current_data = data_np[idx].values
            date = pd.to_datetime(self.df["date"].iloc[idx]).strftime("%Y-%m-%d")
            with rio.open(output_dir / f"{date}.tif", "w", **profile) as dst:
                dst.write((current_data * 10000).astype(np.uint16))  # Save the interpolated image

        return self._spawn(df=self.df, current_dir=output_dir)

    def smooth(
        self,
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "smoothed",
        smooth_w: int = 7,
        smooth_p: int = 2,
        device: str | torch.device = "cpu",
    ) -> "SatCubeMetadata":

        input_dir = pathlib.Path(input_dir).expanduser().resolve() if input_dir else self._dir()
        output_dir = pathlib.Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        all_raw_files = list(input_dir / self.df["outname"])
        out_files = [output_dir / file.name for file in all_raw_files]
    
        profile = rio.open(all_raw_files[0]).profile
        data_np = (np.array([rio.open(file).read() for file in all_raw_files]) / 10000).astype(np.float32)

        data_month = pd.to_datetime(self.df["date"]).dt.month
        data_clim = []
        for month in range(1, 13):
            data_clim.append(data_np[data_month == month].mean(axis=0) / 10000)
        data_clim = np.array(data_clim)

        for idx, month in enumerate(data_month):
            data_np[idx] = data_np[idx] - data_clim[month - 1]

        # Smooth the residuals using Gaussian smoothing
        data_np = torch.from_numpy(data_np).float().to(device)
        try:
            data_np = (
                gaussian_smooth(
                    data_np, kernel_size=smooth_w, sigma=smooth_p
                ).cpu().numpy()
            )
        except Exception as e:
            print(e)
            data_np = data_np.cpu().numpy()

        # Add the residuals back to the climatology
        for idx, month in enumerate(data_month):
            data_np[idx] = data_np[idx] + data_clim[month - 1]

        # Save the smoothed images
        for idx, file in enumerate(out_files):
            with rio.open(file, "w", **profile) as dst:
                    dst.write((data_np[idx] * 10000).astype(np.uint16))

        # Prepare the new table
        new_table = pd.DataFrame(
            {
                "date": self.df["date"],
                "outname": self.df["outname"],
            }
        )

        return self._spawn(df=new_table, current_dir=output_dir)    

    def filter_metadata(self, condition) -> "SatCubeMetadata":
        filtered_df = self.df[condition(self.df)]
        return self._spawn(df=filtered_df, current_dir=self._current_dir)
    
    def __repr__(self) -> str: 
        return self.df.__repr__()
    
    __str__ = __repr__
    
    def _repr_html_(self) -> str:
        html = getattr(self.df, "_repr_html_", None)
        return html() if callable(html) else self.df.__repr__()
    
    def __getattr__(self, item):
        return getattr(self.df, item)

    def __getitem__(self, key):
        if isinstance(key, pd.Series) or isinstance(key, pd.DataFrame): 
            filtered_df = self.df[key]
            return self._spawn(df=filtered_df, current_dir=self._current_dir)
        return self.df[key]
    def __len__(self):
        return len(self.df)
    
    def update_metadata(self, new_df: pd.DataFrame) -> None:
        self.df = new_df