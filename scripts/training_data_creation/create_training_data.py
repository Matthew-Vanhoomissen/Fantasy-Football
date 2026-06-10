import pandas as pd 

from scripts.input_collection.finding_team_data import get_offensive_week_data
from scripts.input_collection.player_stats_data import get_player_week_data
from scripts.input_collection.player_stats_data import get_player_team
from scripts.input_collection.player_stats_data import get_opponent_team
from scripts.input_collection.defensive_team_data import get_defensive_week_data
from scripts.input_collection.collection_methods import create_csvs_offense
from scripts.input_collection.collection_methods import create_csvs_defense

all_data = pd.read_csv("data/play_by_play/play_by_play_2025.csv", low_memory=False)

players = pd.read_csv("data/player_names/players_2025.csv", header=None, skiprows=1, low_memory=False)[0].dropna().unique().tolist()

all_player_data = []

# Iterate through each player
for player_name in players:
    print(player_name)
    
    # Load team data once since offense doesn't change with player
    offensive_team_name = get_player_team(all_data, player_name)
    offensive_team_data, player_data = create_csvs_offense(all_data, player_name, offensive_team_name)
    # Get data for each defense played that week
    for num in range(4, 18):
        week = num

        print(week)
        defensive_team_name = get_opponent_team(all_data, offensive_team_name, week) # Get team name and data
        defensive_team_data = create_csvs_defense(all_data, defensive_team_name)

        # If player has not played or is invalid, skip
        offensive_stats = get_offensive_week_data(offensive_team_name, offensive_team_data, week)
        if offensive_stats is None:
            print(f"No data for week {week}")
            continue

        # If error in reading defensive data, skip
        defensive_stats = get_defensive_week_data(defensive_team_name, defensive_team_data, week)
        if defensive_stats is None:
            print(f"No defensive stats for week {week}")
            continue

        # If error in reading player data, skip
        player_stats = get_player_week_data(player_name, offensive_team_name, player_data, all_data, week)
        if player_stats is None:
            print(f"Player did not participate this week {week}")
            continue

        # Ensure dataframes have differing column names
        offensive_stats = offensive_stats.rename(columns={"team_name": "off_team_name"})
        defensive_stats = defensive_stats.rename(columns={"team_name": "def_team_name"})
        player_stats = player_stats.rename(columns={"team_name": "off_team_name"})  

        player_stats["def_team_name"] = defensive_team_name

        # Merge all three into one row
        final = (
            player_stats
            .merge(offensive_stats, on=["off_team_name", "week"], how="left")  
            .merge(defensive_stats, left_on=["def_team_name", "week"], right_on=["def_team_name", "week"], how="left")  
        )

        all_player_data.append(final)

# Add all entries together
season_data = pd.concat(all_player_data, ignore_index=True)
# final_data = pd.DataFrame(season_data)
# final_data.to_csv("data/training_dataset/training_dataset_2024.csv", index=False)

# Load other seasons to add together
season_2024 = pd.read_csv("data/training_dataset/training_dataset_2024.csv", low_memory=False)
season_2023 = pd.read_csv("data/training_dataset/training_dataset_2023.csv", low_memory=False)
season_2022 = pd.read_csv("data/training_dataset/training_dataset_2022.csv", low_memory=False)

# Add season label
season_data['season'] = 2025
season_2024['season'] = 2024
season_2023['season'] = 2023
season_2022['season'] = 2022

final_data = pd.concat([season_2022, season_2023, season_2024, season_data], ignore_index=True)
final_data.to_csv("data/training_dataset/training_dataset.csv", index=False)
