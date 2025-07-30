from dataclasses import dataclass
from typing import Optional, List


@dataclass
class User:
    name: str
    url: str
    playcount: int
    image: Optional[str]
    raw: dict

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            name=data["name"],
            url=data["url"],
            playcount=int(data["playcount"]),
            image=next((img["#text"] for img in data.get("image", []) if img["size"] == "large"), None),
            raw=data
        )


@dataclass
class Track:
    name: str
    artist: str
    album: Optional[str]
    url: str
    image: Optional[str]
    now_playing: bool = False
    raw: dict = None

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            name=data["name"],
            artist=data["artist"]["name"] if isinstance(data["artist"], dict) else data["artist"],
            album=data.get("album", {}).get("#text"),
            url=data.get("url", ""),
            image=next((img["#text"] for img in data.get("image", []) if img["size"] == "large"), None),
            now_playing=data.get("@attr", {}).get("nowplaying") == "true",
            raw=data
        )


@dataclass
class Album:
    name: str
    artist: str
    url: str
    playcount: int
    image: Optional[str]
    raw: dict

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            name=data["name"],
            artist=data["artist"]["name"] if isinstance(data["artist"], dict) else data["artist"],
            url=data.get("url", ""),
            playcount=int(data.get("playcount", 0)),
            image=next((img["#text"] for img in data.get("image", []) if img["size"] == "large"), None),
            raw=data
        )


@dataclass
class Artist:
    name: str
    url: str
    playcount: int
    image: Optional[str]
    raw: dict

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            name=data["name"],
            url=data.get("url", ""),
            playcount=int(data.get("stats", {}).get("playcount", 0)),
            image=next((img["#text"] for img in data.get("image", []) if img["size"] == "large"), None),
            raw=data
        )
      
