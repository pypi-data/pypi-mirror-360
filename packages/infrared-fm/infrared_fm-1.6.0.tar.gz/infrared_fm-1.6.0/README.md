<p align="center">
  <img src="https://files.catbox.moe/kjr0cd.png" width="720" alt="infrared banner"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/module-infrafm-7a0f17?style=flat&labelColor=000000" />
  <img src="https://img.shields.io/badge/api-last.fm-7a0f17?style=flat&labelColor=000000" />
  <img src="https://img.shields.io/badge/status-private-7a0f17?style=flat&labelColor=000000" />
</p>

<br>

<blockquote align="center">
  <em>maybe we scrobble.<br>maybe we don’t.</em>
</blockquote>

---

### <span style="color:#7a0f17">what is this</span>

**infrared.fm**  
> the last.fm wrapper powering `infrared`  
> built for speed. async. clean.

- user, artist, album, track, and chart endpoints  
- powers dynamic embed views: nowplaying, charts, stats  
- no extra weight, just flex

---

### <span style="color:#7a0f17">how to</span>

```py
import asyncio
from infrafm import LastFMClient

lfm = LastFMClient("your_lastfm_api_key")

async def main():
    track = await lfm.user.get_now_playing("opexwtf")

    if track:
        print(f"🎧 {track.name} — {track.artist}")
    else:
        print("No track playing.")

    await lfm.close()

asyncio.run(main())
