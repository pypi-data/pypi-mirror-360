from ..models import Artist, Track, Album
from ..utils import paginate

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import LastFMClient

class ArtistAPI:
    def __init__(self, client: "LastFMClient"):
        self._client = client

    async def get_info(self, artist: str) -> Artist:
        data = await self._client.request("artist.getinfo", artist=artist)
        return Artist.from_data(data["artist"])

    async def get_top_tracks(self, artist: str, limit: int = 50, pages: int = 1) -> List[Track]:
        return await paginate(
            method="artist.gettoptracks",
            client=self._client,
            key="track",
            model=Track,
            params={"artist": artist, "limit": limit},
            pages=pages,
            subkey="toptracks"
        )

    async def get_top_albums(self, artist: str, limit: int = 50, pages: int = 1) -> List[Album]:
        return await paginate(
            method="artist.gettopalbums",
            client=self._client,
            key="album",
            model=Album,
            params={"artist": artist, "limit": limit},
            pages=pages,
            subkey="topalbums"
        )

    async def get_similar(self, artist: str, limit: int = 10) -> List[Artist]:
        data = await self._client.request("artist.getsimilar", artist=artist, limit=limit)
        return [Artist.from_data(a) for a in data.get("similarartists", {}).get("artist", [])]

    async def get_top_tags(self, artist: str) -> List[str]:
        data = await self._client.request("artist.gettoptags", artist=artist)
        return [tag["name"] for tag in data.get("toptags", {}).get("tag", [])]
