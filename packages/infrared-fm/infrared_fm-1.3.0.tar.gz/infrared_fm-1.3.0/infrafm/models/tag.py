from dataclasses import dataclass
from .base import BaseModel

@dataclass
class Tag(BaseModel):
    name: str = ""
    url: str = ""
    reach: str = ""
    taggings: str = ""
