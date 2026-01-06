import os
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BALLDONTLIE_API_KEY")
if not API_KEY:
    raise ValueError("BALLDONTLIE_API_KEY not found")

BASE_URL = "https://api.balldontlie.io/nfl/v1/players"
OUTPUT_FILE = "../data/nfl_players.csv"
REQUEST_DELAY = 12.5  # 5 RPM
MAX_PLAYERS = 2000

headers = {"Authorization": API_KEY}

players_data = []
cursor = None
page = 0
stop = False  # ← important

while not stop:
    params = {"cursor": cursor, "active": "true"} if cursor else {"active": "true"}

    r = requests.get(BASE_URL, headers=headers, params=params)

    if r.status_code == 429:
        time.sleep(60)
        continue

    r.raise_for_status()
    data = r.json()

    for p in data["data"]:
        players_data.append({
            "first_name": p["first_name"],
            "last_name": p["last_name"],
            "team": p["team"]["abbreviation"] if p.get("team") else None,
            "position": p["position_abbreviation"]
        })
        print(len(players_data))

        if len(players_data) >= MAX_PLAYERS:
            print(f"🛑 Reached max of {MAX_PLAYERS} players.")
            stop = True
            break

    page += 1
    print(f"Page {page}: total players {len(players_data)}")

    if stop:
        break

    cursor = data["meta"]["next_cursor"]
    if cursor is None:
        break

    time.sleep(REQUEST_DELAY)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["first_name", "last_name", "team", "position"]
    )
    writer.writeheader()
    writer.writerows(players_data)

print(f"Saved {len(players_data)} active players")
