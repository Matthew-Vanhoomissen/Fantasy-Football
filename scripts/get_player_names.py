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

headers = {
    "Authorization": API_KEY
}

players_data = []
cursor = None
REQUEST_DELAY = 12.5  # seconds (5 requests per minute)

while True:
    params = {"cursor": cursor} if cursor else {}

    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code == 429:
        print("Rate limited. Sleeping 60 seconds...")
        time.sleep(60)
        continue

    response.raise_for_status()
    data = response.json()

    for player in data["data"]:
        players_data.append({
            "first_name": player["first_name"],
            "last_name": player["last_name"],
            "team": player["team"]["abbreviation"] if player.get("team") else None,
            "position": player["position_abbreviation"]
        })

    cursor = data["meta"]["next_cursor"]
    if cursor is None:
        break

    print(f"Fetched page, sleeping {REQUEST_DELAY}s...")
    time.sleep(REQUEST_DELAY)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["first_name", "last_name", "team", "position"]
    )
    writer.writeheader()
    writer.writerows(players_data)

print(f"Saved {len(players_data)} players to {OUTPUT_FILE}")
