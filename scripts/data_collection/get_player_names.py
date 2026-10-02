import pandas as pd
import os


OUTPUT_FILE = "data/nfl_players.csv"


def get_names(
    season: int
) -> None:
    """
    Pulls the nflverse roster for the input season. The roster includes full names
    along with the GSIS player ID used in the nflFastR play-by-play data, which links
    each full name to its plays without relying on abbreviated names.

    """
    # url to get roster csv for current season
    url = f"https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{season}.csv"

    print(f"Downloading roster data for {season} season from nflverse...")

    try:
        roster = pd.read_csv(url, low_memory=False)
        print(f"Roster successfully downloaded for {season} season.")
    except Exception as e:
        print(f" Error downloading {season} roster. It may not be available yet.")
        print("Error details:", e)
        exit()

    os.makedirs("data", exist_ok=True)

    roster.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Saved {len(roster)} players to {OUTPUT_FILE}")
