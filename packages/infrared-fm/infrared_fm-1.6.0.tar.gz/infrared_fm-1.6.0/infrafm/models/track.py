from dataclasses import dataclass
from .base import BaseModel

@dataclass
class Track(BaseModel):
    name: str = ""
    artist: str = ""
    album: str = ""
    url: str = ""
    duration: str = ""
    listeners: str = ""
    playcount: str = ""
    now_playing: bool = False

    @classmethod
    def from_data(cls, data: dict) -> "Track":
        artist = data.get("artist", {}).get("name") if isinstance(data.get("artist"), dict) else data.get("artist", "")
        album = data.get("album", {}).get("#text", "") if isinstance(data.get("album"), dict) else data.get("album", "")
        now_playing = data.get("@attr", {}).get("nowplaying") == "true"
        return super().from_data({**data, "artist": artist, "album": album, "now_playing": now_playing})
