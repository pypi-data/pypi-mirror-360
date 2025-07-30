from ..models import Track
from ..utils import paginate
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import LastFMClient

class TrackAPI:
    def __init__(self, client: "LastFMClient"):
        self._client = client

    async def get_info(self, artist: str, track: str) -> Track:
        data = await self._client.request("track.getinfo", artist=artist, track=track)
        return Track.from_data(data["track"])

    async def get_similar(self, artist: str, track: str, limit: int = 50) -> List[Track]:
        data = await self._client.request("track.getsimilar", artist=artist, track=track, limit=limit)
        tracks = data["similartracks"]["track"]
        return [Track.from_data(t) for t in tracks]

    async def get_top_tags(self, artist: str, track: str) -> List[str]:
        data = await self._client.request("track.gettoptags", artist=artist, track=track)
        return [tag["name"] for tag in data.get("toptags", {}).get("tag", [])]
