import pathlib
from typing import Tuple
import numpy as np
import pandas as pd
import rasterio as rio
from concurrent.futures import ProcessPoolExecutor, as_completed


def monthly_composites_s2(
    metadata: pd.DataFrame | None = None,   
    input_dir: str | pathlib.Path | None = None,
    output_dir: str | pathlib.Path = "monthly_composites",
    date_range: Tuple[str, str] = ("2018-06-01", "2020-01-01"),
    agg_method: str = "median",
):

    input_dir = pathlib.Path(input_dir).expanduser().resolve()
    output_dir = pathlib.Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    all_raw_files = [input_dir / f for f in input_dir.glob("*.tif") if f.is_file()]

    with rio.open(all_raw_files[0]) as src:
        profile = src.profile


    all_raw_dates = pd.to_datetime(metadata["date"])
    all_raw_date_min = pd.to_datetime(date_range[0])
    all_raw_date_max = pd.to_datetime(date_range[1])
    all_raw_dates_unique = pd.date_range(
        all_raw_date_min, all_raw_date_max, freq="MS"
    ) + pd.DateOffset(days=14)
    all_raw_dates_unique = all_raw_dates_unique.strftime("%Y-%m-15")

    # Aggregate the data considering the method and dates
    new_table = []
    for idx, date in enumerate(all_raw_dates_unique):
        
        # Get the images to aggregate
        idxs = all_raw_dates.dt.strftime("%Y-%m-15") == date
        images = [all_raw_files[i] for i in np.where(idxs)[0]]

        if len(images) == 0:
            data = np.ones((profile["count"], profile["height"], profile["width"]))
            data = 65535 * data
            nodata = 1
            profile_image = profile
        else:
            # Read the images
            container = []
            for image in images:
                with rio.open(image) as src:
                    data = src.read()
                    profile_image = src.profile
                container.append(data)

            # Aggregate the data
            if agg_method == "mean":
                data = np.mean(container, axis=0)
            elif agg_method == "median":
                data = np.median(container, axis=0)
            elif agg_method == "max":
                data = np.max(container, axis=0)
            elif agg_method == "min":
                data = np.min(container, axis=0)
            else:
                raise ValueError("Invalid aggregation method")

            nodata = 0

        # Save the image
        with rio.open(output_dir / f"{date}.tif", "w", **profile_image) as dst:
            dst.write(data.astype(rio.uint16))


        meta_dict = {
            "outname": f"{date}.tif",
            "date": date,
            "nodata": nodata,
        }

        new_table.append(meta_dict)


    return pd.DataFrame(new_table)