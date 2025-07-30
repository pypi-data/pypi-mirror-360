from dataclasses import dataclass
from .base import BaseModel

@dataclass
class Artist(BaseModel):
    name: str = ""
    url: str = ""
    listeners: str = ""
    playcount: str = ""
