# from input_collection.total_data_collection import get_player_input
from input_collection.collection_methods import create_csvs_offense, create_csvs_defense
from input_collection.defensive_team_data import get_defensive_week_data
from input_collection.finding_team_data import get_offensive_week_data
from input_collection.player_stats_data import get_player_week_data

import pandas as pd

all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

player_name = "J.Love"
offensive_team_name = "GB"
defensive_team_name = "NE"
week = 19

defensive_team_data1 = create_csvs_defense(all_data, defensive_team_name)
offensive_team_data1, player_data1 = create_csvs_offense(all_data, player_name, offensive_team_name)

defensive_stats1 = get_defensive_week_data(defensive_team_name, defensive_team_data1, week)
offensive_stats1 = get_offensive_week_data(offensive_team_name, offensive_team_data1, week)
player_stats1 = get_player_week_data(player_name, offensive_team_name, player_data1, all_data, week)

if defensive_stats1 is None or offensive_stats1 is None or player_stats1 is None:
    exit()

offensive_stats1 = offensive_stats1.rename(columns={"team_name": "off_team_name"})
defensive_stats1 = defensive_stats1.rename(columns={"team_name": "def_team_name"})
player_stats1 = player_stats1.rename(columns={"team_name": "off_team_name"})

player_stats1["def_team_name"] = defensive_team_name

data = (
    player_stats1
    .merge(offensive_stats1, on="off_team_name", how="left")
    .merge(defensive_stats1, how="left", left_on="def_team_name", right_on="def_team_name")
)

print(data)
