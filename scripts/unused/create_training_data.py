import pandas as pd 

from finding_team_data import get_offensive_week_data
from player_stats_data import get_player_week_data
from player_stats_data import get_player_team
from player_stats_data import get_opponent_team
from defensive_team_data import get_defensive_week_data
from make_csv import create_csvs_offense
from make_csv import create_csvs_defense

all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

players = pd.read_csv("../data/players.csv", header=None, skiprows=1, low_memory=False)[0].dropna().unique().tolist()

all_player_data = []

for player_name in players:
    print(player_name)
    
    offensive_team_name = get_player_team(all_data, player_name)
    offensive_team_data3, player_data3 = create_csvs_offense(all_data, player_name, offensive_team_name)
    for num in range(4, 12):
        week = num

        print(week)
        defensive_team_name = get_opponent_team(all_data, offensive_team_name, week)
        defensive_team_data3 = create_csvs_defense(all_data, defensive_team_name)

        offensive_stats3 = get_offensive_week_data(offensive_team_name, offensive_team_data3, week)
        if offensive_stats3 is None:
            print(f"No data for week {week}")
            continue

        defensive_stats3 = get_defensive_week_data(defensive_team_name, defensive_team_data3, week)
        if defensive_stats3 is None:
            print(f"No defensive stats for week {week}")
            continue

        player_stats3 = get_player_week_data(player_name, offensive_team_name, player_data3, all_data, week)
        if player_stats3 is None:
            print(f"Player did not participate this week {week}")
            continue

        offensive_stats3 = offensive_stats3.rename(columns={"team_name": "off_team_name"})
        defensive_stats3 = defensive_stats3.rename(columns={"team_name": "def_team_name"})
        player_stats3 = player_stats3.rename(columns={"team_name": "off_team_name"})  

        player_stats3["def_team_name"] = defensive_team_name

        # Merge all three into one row
        final3 = (
            player_stats3
            .merge(offensive_stats3, on=["off_team_name", "week"], how="left")  
            .merge(defensive_stats3, left_on=["def_team_name", "week"], right_on=["def_team_name", "week"], how="left")  
        )

        all_player_data.append(final3)

season_data = pd.concat(all_player_data, ignore_index=True)

season_2024 = pd.read_csv("../data/training_dataset_2024.csv", low_memory=False)

season_data['season'] = 2025
season_2024['season'] = 2024
final_data = pd.concat([season_2024, season_data], ignore_index=True)
final_data.to_csv("../data/training_dataset.csv", index=False)
