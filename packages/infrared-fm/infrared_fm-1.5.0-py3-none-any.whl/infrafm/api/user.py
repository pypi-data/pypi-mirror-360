from ..models import User, Track
from ..utils import paginate
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import LastFMClient

class UserAPI:
    def __init__(self, client: "LastFMClient"):
        self._client = client

    async def get_info(self, user: str) -> User:
        data = await self._client.request("user.getinfo", user=user)
        return User.from_data(data["user"])

    async def get_recent_tracks(self, user: str, limit: int = 50, pages: int = 1) -> List[Track]:
        return await paginate(
            method="user.getrecenttracks",
            client=self._client,
            key="track",
            model=Track,
            params={"user": user, "limit": limit},
            pages=pages,
            subkey="recenttracks"
        )

    async def get_now_playing(self, user: str) -> Optional[Track]:
        data = await self._client.request("user.getrecenttracks", user=user, limit=1)
        tracks = data.get("recenttracks", {}).get("track", [])
        if not tracks:
            return None

        track_data = tracks[0]
        now_playing = track_data.get("@attr", {}).get("nowplaying") == "true"
        if now_playing:
            return Track.from_data(track_data)
        return None

