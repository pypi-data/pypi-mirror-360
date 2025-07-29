import sys, time, threading, itertools
import cubexpress as ce
import pandas as pd
from satcube.objects import SatCubeMetadata
import pathlib

def download(
    lon: float,
    lat: float,
    edge_size: int,
    start: str,
    end: str,
    *,
    max_cscore: float = 1,
    min_cscore: float = 0,
    outfolder: str = "raw",
    nworks: int = 4
) -> "SatCubeMetadata":
        
        
    outfolder = pathlib.Path(outfolder).resolve()

    table = ce.s2_table(
        lon=lon,
        lat=lat,
        edge_size=edge_size,
        start=start,
        end=end,
        max_cscore=max_cscore,
        min_cscore=min_cscore
    )   
        
    requests = ce.table_to_requestset(
        table=table,
        mosaic=True
    )
    
    ce.get_cube(
        requests=requests,
        outfolder=outfolder,
        nworks=nworks
    )

    table_req = (
        requests._dataframe.copy()
        .drop(columns=['geotransform', 'manifest', 'outname', 'width', 'height', 'scale_x', 'scale_y'])
    )
    
    table_req['date'] = table_req['id'].str.split('_').str[0]

    result_table = (
        table.groupby('date')
        .agg(
            id=('id', lambda x: '-'.join(x)),
            cs_cdf=('cs_cdf', 'first')
        )
        .reset_index()  
    )
    
    table_final = table_req.merge(
        result_table,
        on='date',
        how='left'
    ).rename(columns={'id_x': 'id', 'id_y': 'gee_ids'})

    table_final.to_csv(outfolder / "metadata.csv", index=False)

    return SatCubeMetadata(df=table_final, raw_dir=outfolder)
