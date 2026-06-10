import pandas as pd
import os


season = 2025
DATA_DIR = "../data"

url = "https://github.com/nflverse/nfldata/raw/master/data/games.csv"

print("Downloading NFL schedules from nflverse...")


try:
    schedules = pd.read_csv(url, low_memory=False)
    print(f"Downloaded {len(schedules)} total games")
    print(f"Seasons available: {sorted(schedules['season'].unique())}")
except Exception as e:
    print("Error downloading schedules.")
    print("Error details:", e)
    exit()


season_schedule = schedules[schedules["season"] == season]

if season_schedule.empty:
    print(f"No schedule found for season {season}.")
    exit()

season_schedule = season_schedule[season_schedule["game_type"] == "REG"]

print(f"Found {len(season_schedule)} regular season games for {season}")


os.makedirs(DATA_DIR, exist_ok=True)

output_path = f"{DATA_DIR}/schedule_{season}.csv"
season_schedule.to_csv(output_path, index=False)

print(f"✅ Saved {len(season_schedule)} games to {output_path}")