from dataclasses import dataclass
from .base import BaseModel

@dataclass
class User(BaseModel):
    name: str = ""
    url: str = ""
    playcount: str = ""
    country: str = ""
    registered: dict = None
