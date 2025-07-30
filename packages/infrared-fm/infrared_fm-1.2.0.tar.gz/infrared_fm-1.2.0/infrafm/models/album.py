from dataclasses import dataclass
from .base import BaseModel

@dataclass
class Album(BaseModel):
    name: str = ""
    artist: str = ""
    url: str = ""
    playcount: str = ""
    listeners: str = ""
