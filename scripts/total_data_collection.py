import pandas as pd

from defensive_team_data import get_defensive_data
from finding_team_data import get_offensive_data
from player_stats_data import get_player_data


team_data = pd.read_csv("../data/team_data_2025.csv", low_memory=False)
player_data = pd.read_csv("../data/player1_data_2025.csv", low_memory=False)
all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

player_name = "T.Kraft"
team_name = "GB"

defensive_stats = get_defensive_data(team_name, team_data)
offensive_stats = get_offensive_data(team_name, team_data)
player_stats = get_player_data(player_name, team_name, player_data, all_data)

final = player_stats.merge(offensive_stats, on="team_name", how="left") \
                    .merge(defensive_stats, on="team_name", how="left") \
                    .merge(player_stats, on="team_name", how="left")
print(final)
