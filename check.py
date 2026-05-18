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
finish_time = room.get("finish_time", 0)
replay = room.get("replay", False)
title = room.get("title", "").replace('"', "").replace("\n", "")

# Live = stream actief (status 2) EN nog niet geëindigd
# Of status 4 maar dan alleen als replay=False en finish_time=0
is_live = (status == 2 and finish_time == 0 and not replay) or           (status == 4 and finish_time == 0 and not replay and user_count > 0)

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
result = {"isLive": is_live, "title": title, "viewerCount": user_count, "updatedAt": now}

with open("status.json", "w") as f:
    json.dump(result, f)

print(f"Live: {is_live} | Status: {status} | Replay: {replay} | Finish: {finish_time} | Viewers: {user_count}")
