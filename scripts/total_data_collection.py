import pandas as pd

from defensive_team_data import get_defensive_data
from finding_team_data import get_offensive_data
from player_stats_data import get_player_data
from make_csv import create_csvs_defense, create_csvs_offense


all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

player_name = "T.Kraft"
offensive_team_name = "GB"
defensive_team_name = "PHI"

defensive_team_data1 = create_csvs_defense(all_data, defensive_team_name)
offensive_team_data1, player_data1 = create_csvs_offense(all_data, player_name, offensive_team_name)

defensive_stats1 = get_defensive_data(defensive_team_name, defensive_team_data1)
offensive_stats1 = get_offensive_data(offensive_team_name, offensive_team_data1)
player_stats1 = get_player_data(player_name, offensive_team_name, player_data1, all_data)


offensive_stats1 = offensive_stats1.rename(columns={"team_name": "off_team_name"})
defensive_stats1 = defensive_stats1.rename(columns={"team_name": "def_team_name"})
player_stats1 = player_stats1.rename(columns={"team_name": "off_team_name"})  

player_stats1["def_team_name"] = defensive_team_name

final1 = (
    player_stats1
    .merge(offensive_stats1, on="off_team_name", how="left")
    .merge(defensive_stats1, how="left", left_on="def_team_name", right_on="def_team_name")
)

print(final1)