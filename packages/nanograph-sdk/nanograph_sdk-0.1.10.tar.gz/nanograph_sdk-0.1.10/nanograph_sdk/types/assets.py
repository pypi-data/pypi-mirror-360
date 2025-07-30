from typing import TypedDict, Dict, Union, BinaryIO, Optional
from io import IOBase

class Asset(TypedDict):
    uuid: str
    name: str
    type: str
    hash: str
    size: int
    created_at: Optional[str]
    meta: Optional[Dict]
    uri: Optional[str]

class AssetFilter(TypedDict, total=False):
    type: str
    hash: str

class ResolveAssetOptions(TypedDict, total=False):
    as_buffer: bool

class UploadAssetOptions(TypedDict, total=False):
    type: str
    meta: Dict
    filename: str  # Optional because TypedDict with total=False

class AssetRef(TypedDict):
    domain: str
    uuid: str

class AssetPresignedUrl(TypedDict):
    url: str
    expiresIn: int

# Type aliases
AssetUploadInput = Union[str, bytes, BinaryIO, IOBase]
AssetUploadResult = Asset 