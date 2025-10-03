# script que trae los posts y los guarda.

import time
from typing import Any, Dict, List, Optional

import requests

from .db import insert_posts


REDDIT_NEW_URL = "https://www.reddit.com/r/aww/new.json?limit=100"
USER_AGENT = "reddit-aww-viewer/1.0 (by u/yourusername)"
#from backend.fetch_posts import fetch_and_store_posts
#fetch_and_store_posts()

def _safe_thumbnail(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    invalids = {"self", "default", "nsfw", "image", "spoiler"}
    if value.lower() in invalids:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return None


def _parse_posts(resp_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    children = resp_json.get("data", {}).get("children", [])
    parsed: List[Dict[str, Any]] = []
    for child in children:
        data = child.get("data", {})
        post_id = data.get("id")
        title = data.get("title")
        selftext = data.get("selftext") or ""
        thumbnail = _safe_thumbnail(data.get("thumbnail"))
        permalink = data.get("permalink")
        link = f"https://reddit.com{permalink}" if permalink else None
        created_utc = data.get("created_utc")

        if not (post_id and title and link and isinstance(created_utc, (int, float))):
            continue

        parsed.append(
            {
                "id": post_id,
                "title": title,
                "text": selftext,
                "thumbnail": thumbnail,
                "link": link,
                "created_utc": int(created_utc),
            }
        )
    return parsed


def fetch_and_store_posts() -> int:
    """Fetch latest posts from r/aww, filter last hour, insert into SQLite.

    Returns the number of posts inserted.
    """
    try:
        response = requests.get(
            REDDIT_NEW_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"[fetch_posts] Request failed: {exc}")
        return 0
    except ValueError as exc:
        print(f"[fetch_posts] Failed to decode JSON: {exc}")
        return 0

    all_posts = _parse_posts(data)
    one_hour_ago = int(time.time()) - 3600
    recent_posts = [p for p in all_posts if p["created_utc"] > one_hour_ago]

    if not recent_posts:
        return 0

    inserted = insert_posts(recent_posts)
    return inserted


if __name__ == "__main__":
    count = fetch_and_store_posts()
    print(f"Inserted {count} new posts")
