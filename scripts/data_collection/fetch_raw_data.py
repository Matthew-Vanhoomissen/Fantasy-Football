import pandas as pd
import os

# current year
season = 2025

# url to get csv for current season
url = f"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"

print(f"Downloading play-by-play data for {season} season from nflfastR...")

try:
    pbp = pd.read_csv(url, compression="gzip", low_memory=False)
    print(f"Data successfully downloaded for {season} season.")
except Exception as e:
    print(f" Error downloading {season} data. It may not be available yet.")
    print("Error details:", e)
    exit()

os.makedirs("../data", exist_ok=True)

output_path = f"../data/play_by_play_{season}.csv"
pbp.to_csv(output_path, index=False)
print(f"Data saved to {output_path}")