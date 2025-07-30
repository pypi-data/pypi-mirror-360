from typing import List
from ..client import LastFMClient
from ..models.track import Track
from ..models.artist import Artist
from ..models.tag import Tag
from ..utils import paginate

class ChartAPI:
    def __init__(self, client: LastFMClient):
        self._client = client

    async def get_top_tracks(self, limit: int = 50, pages: int = 1) -> List[Track]:
        return await paginate(
            method="chart.gettoptracks",
            client=self._client,
            key="track",
            model=Track,
            params={"limit": limit},
            pages=pages,
            subkey="tracks"
        )

    async def get_top_artists(self, limit: int = 50, pages: int = 1) -> List[Artist]:
        return await paginate(
            method="chart.gettopartists",
            client=self._client,
            key="artist",
            model=Artist,
            params={"limit": limit},
            pages=pages,
            subkey="artists"
        )

    async def get_top_tags(self, limit: int = 50) -> List[Tag]:
        data = await self._client.request("chart.gettoptags", limit=limit)
        return [Tag.from_data(tag) for tag in data.get("tags", {}).get("tag", [])]
