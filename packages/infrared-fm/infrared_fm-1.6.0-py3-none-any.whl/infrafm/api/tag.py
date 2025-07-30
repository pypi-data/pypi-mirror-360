from ..models import Tag, Track, Artist, Album
from ..utils import paginate
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import LastFMClient

class TagAPI:
    def __init__(self, client: "LastFMClient"):
        self._client = client

    async def get_info(self, tag: str) -> Tag:
        data = await self._client.request("tag.getinfo", tag=tag)
        return Tag.from_data(data["tag"])

    async def get_top_tracks(self, tag: str, limit: int = 50, pages: int = 1) -> List[Track]:
        return await paginate(
            method="tag.gettoptracks",
            client=self._client,
            key="track",
            model=Track,
            params={"tag": tag, "limit": limit},
            pages=pages,
            subkey="tracks"
        )

    async def get_top_artists(self, tag: str, limit: int = 50, pages: int = 1) -> List[Artist]:
        return await paginate(
            method="tag.gettopartists",
            client=self._client,
            key="artist",
            model=Artist,
            params={"tag": tag, "limit": limit},
            pages=pages,
            subkey="topartists"
        )

    async def get_top_albums(self, tag: str, limit: int = 50, pages: int = 1) -> List[Album]:
        return await paginate(
            method="tag.gettopalbums",
            client=self._client,
            key="album",
            model=Album,
            params={"tag": tag, "limit": limit},
            pages=pages,
            subkey="albums"
        )

    async def get_similar(self, tag: str) -> List[Tag]:
        data = await self._client.request("tag.getsimilar", tag=tag)
        return [Tag.from_data(t) for t in data.get("similartags", {}).get("tag", [])]
