# satcube/objects.py
from __future__ import annotations
from dataclasses import dataclass, field
import pathlib
import pandas as pd

from satcube.align  import align as _align_fn
from satcube.cloud_detection  import cloud_masking as _cloud_fn

@dataclass
class SatCubeMetadata:
    df: pd.DataFrame = field(repr=False)
    raw_dir: pathlib.Path = field(repr=False)

    def __repr__(self) -> str: 
        return self.df.__repr__()
    
    __str__ = __repr__
    
    def _repr_html_(self) -> str:
        html = getattr(self.df, "_repr_html_", None)
        return html() if callable(html) else self.df.__repr__()

    def align(
        self,
        input_dir: str | pathlib.Path | None = None,
        output_dir: str | pathlib.Path = "aligned",
        nworks: int = 4,
        cache: bool = False
    ) -> "SatCubeMetadata":
        
        if input_dir is None:
            input_dir = self.raw_dir
        else:
            input_dir = pathlib.Path(input_dir).expanduser().resolve()

        _align_fn(
            input_dir=input_dir, 
            output_dir=output_dir, 
            nworks=nworks, 
            cache=cache
        )
        self.aligned_dir = pathlib.Path(output_dir).resolve()
        return self

    def cloud_masking(
        self,
        output_dir: str | pathlib.Path = "masked",
        model_path: str | pathlib.Path = "SEN2CloudEnsemble",
        device: str = "cpu"
    ) -> "SatCubeMetadata":
        if not hasattr(self, "aligned_dir"):
            raise RuntimeError("You must run .align() first")
        _cloud_fn(
            input=self.aligned_dir,
            output=output_dir,
            model_path=model_path,
            device=device
        )
        self.masked_dir = pathlib.Path(output_dir).resolve()
        return self
    
    def __getattr__(self, item):
        return getattr(self.df, item)

    def __getitem__(self, key):
        return self.df.__getitem__(key)
    
    def __len__(self):
        return len(self.df)
    