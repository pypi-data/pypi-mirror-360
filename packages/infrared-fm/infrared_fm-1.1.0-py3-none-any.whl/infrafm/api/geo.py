from typing import List
from ..client import LastFMClient
from ..models.artist import Artist
from ..models.track import Track
from ..utils import paginate

class GeoAPI:
    def __init__(self, client: LastFMClient):
        self._client = client

    async def get_top_artists(self, country: str, limit: int = 50, pages: int = 1) -> List[Artist]:
        return await paginate(
            method="geo.gettopartists",
            client=self._client,
            key="artist",
            model=Artist,
            params={"country": country, "limit": limit},
            pages=pages,
            subkey="topartists"
        )

    async def get_top_tracks(self, country: str, location: str = "", limit: int = 50, pages: int = 1) -> List[Track]:
        return await paginate(
            method="geo.gettoptracks",
            client=self._client,
            key="track",
            model=Track,
            params={"country": country, "location": location, "limit": limit},
            pages=pages,
            subkey="tracks"
        )
