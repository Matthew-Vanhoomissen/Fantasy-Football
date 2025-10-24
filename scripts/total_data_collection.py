import pandas as pd

from defensive_team_data import get_defensive_data
from finding_team_data import get_offensive_data
from player_stats_data import get_player_data
from player_stats_data import get_player_week_data
from make_csv import create_csvs

all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

player_name = "T.Kraft"
offensive_team_name = "GB"
defensive_team_name = "PIT"

player_name2 = "J.Love"
offensive_team_name2 = "GB"
defensive_team_name2 = "DET"

create_csvs(player_name, offensive_team_name, defensive_team_name, 1)
create_csvs(player_name2, offensive_team_name2, defensive_team_name2, 2)


offensive_team_data1 = pd.read_csv("../data/offensive_team1.csv", low_memory=False)
defensive_team_data1 = pd.read_csv("../data/defensive_team1.csv", low_memory=False)
player_data1 = pd.read_csv("../data/player_data_1.csv", low_memory=False)

offensive_team_data2 = pd.read_csv("../data/offensive_team2.csv", low_memory=False)
defensive_team_data2 = pd.read_csv("../data/defensive_team2.csv", low_memory=False)
player_data2 = pd.read_csv("../data/player_data_2.csv", low_memory=False)

defensive_stats1 = get_defensive_data(defensive_team_name, defensive_team_data1)
offensive_stats1 = get_offensive_data(offensive_team_name, offensive_team_data1)
player_stats1 = get_player_data(player_name, offensive_team_name, player_data1, all_data)

defensive_stats2 = get_defensive_data(defensive_team_name2, defensive_team_data2)
offensive_stats2 = get_offensive_data(offensive_team_name2, offensive_team_data2)
player_stats2 = get_player_data(player_name2, offensive_team_name2, player_data2, all_data)

offensive_stats1 = offensive_stats1.rename(columns={"team_name": "off_team_name"})
defensive_stats1 = defensive_stats1.rename(columns={"team_name": "def_team_name"})
player_stats1 = player_stats1.rename(columns={"team_name": "off_team_name"})  

offensive_stats2 = offensive_stats2.rename(columns={"team_name": "off_team_name"})
defensive_stats2 = defensive_stats2.rename(columns={"team_name": "def_team_name"})
player_stats2 = player_stats2.rename(columns={"team_name": "off_team_name"}) 

player_stats1["def_team_name"] = defensive_team_name
player_stats2["def_team_name"] = defensive_team_name2


final1 = (
    player_stats1
    .merge(offensive_stats1, on="off_team_name", how="left")
    .merge(defensive_stats1, how="left", left_on="def_team_name", right_on="def_team_name")
)
final2 = (
    player_stats2
    .merge(offensive_stats2, on="off_team_name", how="left")
    .merge(defensive_stats2, how="left", left_on="def_team_name", right_on="def_team_name")
)

all_stats = pd.concat([final1, final2], ignore_index=True)
print(all_stats)


