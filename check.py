import urllib.request, json, re
from datetime import datetime, timezone

# Stap 1: haal room_id dynamisch op via profiel pagina
try:
    req = urllib.request.Request(
        "https://www.tiktok.com/@eubadmah/live",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode("utf-8", errors="ignore")
    match = re.search(r'"roomId"\s*:\s*"?(\d+)"?', html)
    room_id = match.group(1) if match else None
except Exception as e:
    room_id = None
    print(f"Profile fetch error: {e}")

if not room_id:
    print("No room_id found, writing offline")
    result = {"isLive": False, "title": "", "viewerCount": 0, "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open("status.json", "w") as f:
        json.dump(result, f)
    exit()

# Stap 2: check live status
req2 = urllib.request.Request(
    f"https://webcast.tiktok.com/webcast/room/info/?room_id={room_id}&aid=1988",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req2, timeout=10) as r:
    data = json.loads(r.read())

room = data.get("data", {})
status = room.get("status", 0)
user_count = room.get("user_count", 0)
title = room.get("title", "").replace('"', "").replace("\n", "")

is_live = status == 2
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
result = {"isLive": is_live, "title": title, "viewerCount": user_count, "updatedAt": now}

with open("status.json", "w") as f:
    json.dump(result, f)

print(f"RoomID: {room_id} | Live: {is_live} | Status: {status} | Viewers: {user_count}")
