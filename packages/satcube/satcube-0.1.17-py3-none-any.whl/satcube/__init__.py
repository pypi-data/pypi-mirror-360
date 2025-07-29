from satcube.cloud_detection import cloud_masking
from satcube.download import download
from satcube.align import align
import importlib.metadata
from satcube.objects  import SatCubeMetadata  

__all__ = ["cloud_masking", "download", "align", "SatCubeMetadata"]
# __version__ = importlib.metadata.version("satcube")

