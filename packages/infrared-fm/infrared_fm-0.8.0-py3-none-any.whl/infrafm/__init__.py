import aiohttp
from typing import Optional, List, Literal
from .models import User, Track, Album, Artist

BASE = "https://ws.audioscrobbler.com/2.0/"
Period = Literal["7day", "1month", "3month", "6month", "12month", "overall"]


class LastFM:
    def __init__(self, api_key: str, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession()
        self._owns_session = session is None

    async def _get(self, method: str, **params) -> dict:
        query = {
            "method": method,
            "api_key": self.api_key,
            "format": "json",
            **params
        }
        async with self.session.get(BASE, params=query) as resp:
            data = await resp.json()
            if "error" in data:
                raise RuntimeError(f"LastFM API error: {data.get('message')}")
            return data

    
    async def get_user_info(self, username: str) -> User:
        data = await self._get("user.getinfo", user=username)
        return User.from_data(data["user"])

    async def now_playing(self, username: str) -> Optional[Track]:
        data = await self._get("user.getrecenttracks", user=username, limit=1)
        tracks = data.get("recenttracks", {}).get("track", [])
        if not tracks:
            return None
        return Track.from_data(tracks[0])

    async def get_top_albums(self, username: str, period: Period = "7day", limit: int = 9) -> List[Album]:
        data = await self._get("user.gettopalbums", user=username, period=period, limit=limit)
        return [Album.from_data(a) for a in data.get("topalbums", {}).get("album", [])]

    async def get_top_artists(self, username: str, period: Period = "7day", limit: int = 9) -> List[Artist]:
        data = await self._get("user.gettopartists", user=username, period=period, limit=limit)
        return [Artist.from_data(a) for a in data.get("topartists", {}).get("artist", [])]

    async def get_top_tracks(self, username: str, period: Period = "7day", limit: int = 9) -> List[Track]:
        data = await self._get("user.gettoptracks", user=username, period=period, limit=limit)
        return [Track.from_data(t) for t in data.get("toptracks", {}).get("track", [])]

     
    async def get_album_info(self, artist: str, album: str) -> Album:
        data = await self._get("album.getinfo", artist=artist, album=album)
        return Album.from_data(data["album"])

    async def get_artist_info(self, artist: str) -> Artist:
        data = await self._get("artist.getinfo", artist=artist)
        return Artist.from_data(data["artist"])

    async def get_track_info(self, artist: str, track: str) -> Track:
        data = await self._get("track.getinfo", artist=artist, track=track)
        return Track.from_data(data["track"])

    async def close(self):
        if self._owns_session:
            await self.session.close()
  
