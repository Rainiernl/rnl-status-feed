import urllib.request, json, re
from datetime import datetime, timezone

# status.json wordt alleen herschreven als er iets verandert dat de perspagina toont.
# Zonder die rem levert elke run een commit op, ook als er dagen niets gebeurt.
#
# De pagina leest isLive altijd, en title plus viewerCount alleen tijdens een stream.
# Daarom telt een kijkersaantal alleen mee als de zender live is en het verschil
# groot genoeg is om op te vallen. Anders zou elke voorbijganger een commit opleveren.

DREMPEL_ABSOLUUT = 5      # minder dan vijf kijkers verschil is ruis
DREMPEL_RELATIEF = 0.15   # of vijftien procent, wat bij grote aantallen eerder telt


def lees_huidig():
    try:
        with open("status.json") as f:
            return json.load(f)
    except Exception:
        return None


def noemenswaardig(oud, nieuw):
    verschil = abs(nieuw - oud)
    return verschil >= max(DREMPEL_ABSOLUUT, oud * DREMPEL_RELATIEF)


def schrijf(is_live, title, viewers):
    huidig = lees_huidig()
    if huidig is not None:
        zelfde_status = huidig.get("isLive") == is_live
        zelfde_titel = huidig.get("title", "") == title
        oud_aantal = huidig.get("viewerCount", 0)
        # Offline doet het aantal er niet toe, de pagina laat het dan niet zien.
        aantal_telt = is_live and noemenswaardig(oud_aantal, viewers)
        if zelfde_status and zelfde_titel and not aantal_telt:
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
