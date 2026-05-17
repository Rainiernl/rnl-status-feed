import urllib.request, json
from datetime import datetime, timezone

req = urllib.request.Request(
    "https://webcast.tiktok.com/webcast/room/info/?room_id=7640508446380378901&aid=1988",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())

room = data.get("data", {})
status = room.get("status", 0)
user_count = room.get("user_count", 0)
title = room.get("title", "").replace('"', "").replace("\n", "")

# Live alleen als er echt kijkers zijn
is_live = user_count > 0 and status in (2, 4)
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

result = {"isLive": is_live, "title": title, "viewerCount": user_count, "updatedAt": now}
with open("status.json", "w") as f:
    json.dump(result, f)

print(f"Live: {is_live} | Status: {status} | Viewers: {user_count} | Title: {title}")
