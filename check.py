import urllib.request, json, re, os
from datetime import datetime, timezone

# Schrijft status.json alleen opnieuw als er inhoudelijk iets veranderd is.
# Anders levert elke run een commit op, ook als de status al dagen hetzelfde is.
# updatedAt is daarmee het moment van de laatste verandering, niet van de laatste check.
# Hoe vers de check zelf is, blijkt uit de runs van de workflow.

def lees_huidig():
    try:
        with open("status.json") as f:
            return json.load(f)
    except Exception:
        return None

def schrijf(is_live, title, viewers):
    huidig = lees_huidig()
    if huidig and (
        huidig.get("isLive") == is_live
        and huidig.get("title", "") == title
        and huidig.get("viewerCount", 0) == viewers
    ):
        print(f"Ongewijzigd (live={is_live}, viewers={viewers}), niets weggeschreven")
        return
    resultaat = {
        "isLive": is_live,
        "title": title,
        "viewerCount": viewers,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open("status.json", "w") as f:
        json.dump(resultaat, f)
    print(f"Gewijzigd, weggeschreven: live={is_live}, viewers={viewers}")

# Stap 1: room_id dynamisch ophalen via de profielpagina
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
    print("No room_id found, offline")
    schrijf(False, "", 0)
    raise SystemExit

# Stap 2: live-status controleren
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
print(f"RoomID: {room_id} | Live: {is_live} | Status: {status} | Viewers: {user_count}")
schrijf(is_live, title, user_count)
