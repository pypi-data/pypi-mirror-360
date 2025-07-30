from ..models import Album
from ..utils import paginate
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import LastFMClient

class AlbumAPI:
    def __init__(self, client: "LastFMClient"):
        self._client = client

    async def get_info(self, artist: str, album: str) -> Album:
        data = await self._client.request("album.getinfo", artist=artist, album=album)
        return Album.from_data(data["album"])

    async def get_top_tags(self, artist: str, album: str) -> List[str]:
        data = await self._client.request("album.gettoptags", artist=artist, album=album)
        return [tag["name"] for tag in data.get("toptags", {}).get("tag", [])]
