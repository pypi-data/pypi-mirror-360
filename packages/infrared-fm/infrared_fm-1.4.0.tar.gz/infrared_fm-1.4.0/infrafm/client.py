import aiohttp
from typing import Any, Dict, Optional

from .exceptions import LastFMAPIError, LastFMHTTPError
from .api import UserAPI, TrackAPI, AlbumAPI, ArtistAPI, TagAPI, GeoAPI, ChartAPI


class LastFMClient:
    def __init__(self, api_key: str, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession()

        
        self.user = UserAPI(self)
        self.track = TrackAPI(self)
        self.album = AlbumAPI(self)
        self.artist = ArtistAPI(self)
        self.tag = TagAPI(self)
        self.geo = GeoAPI(self)
        self.chart = ChartAPI(self)

    async def request(self, method: str, **params) -> Dict[str, Any]:
        url = "https://ws.audioscrobbler.com/2.0/"
        payload = {
            "method": method,
            "api_key": self.api_key,
            "format": "json",
            **params,
        }

        async with self.session.get(url, params=payload) as response:
            if response.status != 200:
                raise LastFMHTTPError(response.status, await response.text())

            data = await response.json()
            if "error" in data:
                raise LastFMAPIError(data["error"], data.get("message", "Unknown API error"))

            return data

    async def close(self):
        await self.session.close()
