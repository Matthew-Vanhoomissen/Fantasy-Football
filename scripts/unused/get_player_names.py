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
REQUEST_DELAY = 12.5  
SAVE_INTERVAL = 10  

headers = {"Authorization": API_KEY}


def save_players(players_data, filename):
    """Save players to CSV file"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["first_name", "last_name", "team", "position"]
        )
        writer.writeheader()
        writer.writerows(players_data)
    print(f"💾 Saved {len(players_data)} players to {filename}")


players_data = []
cursor = None
page = 0

while True:
    params = {"cursor": cursor, "active": "true"} if cursor else {"active": "true"}

    r = requests.get(BASE_URL, headers=headers, params=params)

    if r.status_code == 429:
        print("⏳ Rate limited, waiting 60s...")
        time.sleep(60)
        continue

    r.raise_for_status()
    data = r.json()

    for p in data["data"]:
        # Only include players with a team AND known position
        if p.get("team") and p["position_abbreviation"] != "UNK":
            players_data.append({
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "team": p["team"]["abbreviation"],
                "position": p["position_abbreviation"]
            })

    page += 1
    print(f"Page {page}: total valid players: {len(players_data)}")

    if page % SAVE_INTERVAL == 0:
        save_players(players_data, OUTPUT_FILE)

    cursor = data["meta"]["next_cursor"]
    if cursor is None:
        print("✅ Reached end of data")
        break

    time.sleep(REQUEST_DELAY)

# Final save
save_players(players_data, OUTPUT_FILE)
print(f"✅ Complete! Total: {len(players_data)} active players with teams and known positions")