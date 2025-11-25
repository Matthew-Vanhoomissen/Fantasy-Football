from player_stats_data import get_player_week_data, get_player_data
from defensive_team_data import get_defensive_week_data
from finding_team_data import get_offensive_week_data

from make_csv import create_csvs_offense, create_csvs_defense
from total_data_collection import get_player_input

import pandas as pd
import numpy as np
import pickle

all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)
player_name = "J.Chase"
offensive_team_name = "CIN"
defensive_team_name = "JAX"

defensive_team_data1 = create_csvs_defense(all_data, defensive_team_name)
offensive_team_data1, player_data1 = create_csvs_offense(all_data, player_name, offensive_team_name)

week_data = get_player_week_data(player_name, offensive_team_name, offensive_team_data1, all_data, 8)
offense_week = get_offensive_week_data(offensive_team_name, offensive_team_data1, 8)
defense_week = get_defensive_week_data(defensive_team_name, defensive_team_data1, 8)

offense_week = offense_week.rename(columns={"team_name": "off_team_name"})
defense_week = defense_week.rename(columns={"team_name": "def_team_name"})
week_data = week_data.rename(columns={"team_name": "off_team_name"})

week_data["def_team_name"] = defensive_team_name

data = (
    week_data
    .merge(offense_week, on="off_team_name", how="left")
    .merge(defense_week, how="left", left_on="def_team_name", right_on="def_team_name")
)

# Feature engineering (same as before)
data['bust_adjusted_avg'] = data['average_fantasy_points'] * (1 - data['bust_percent'])
data['recent_momentum'] = data['average_fantasy_points'] + data['last_three_weeks_diff']
data['boom_weighted_avg'] = data['average_fantasy_points'] * (1 + data['boom_percent'])
data['total_usage'] = data['passing_target_percentage'] + data['rushing_percentage']
data['boom_bust_ratio'] = data['boom_percent'] / (data['bust_percent'] + 0.01)
data['td_rate'] = (data['passing_tds_avg'] + data['rushing_tds_avg'] + data['recieving_tds_avg'])
data['matchup_advantage'] = data['epa_per_play'] - data['avg_epa_against']
data['offensive_efficiency'] = data['epa_per_play'] * data['total_usage']
data['recent_volatility'] = abs(data['last_three_weeks_diff'])
data['boom_potential'] = data['boom_points_average'] - data['average_fantasy_points']
data['bust_risk'] = data['average_fantasy_points'] - data['bust_points_average']
data['variance_score'] = (data['boom_percent'] + data['bust_percent']) * data['average_fantasy_points']


total_data = get_player_input(player_name, offensive_team_name, defensive_team_name, all_data)
# Feature engineering (same as before)
total_data['bust_adjusted_avg'] = total_data['average_fantasy_points'] * (1 - total_data['bust_percent'])
total_data['recent_momentum'] = total_data['average_fantasy_points'] + total_data['last_three_weeks_diff']
total_data['boom_weighted_avg'] = total_data['average_fantasy_points'] * (1 + total_data['boom_percent'])
total_data['total_usage'] = total_data['passing_target_percentage'] + total_data['rushing_percentage']
total_data['boom_bust_ratio'] = total_data['boom_percent'] / (total_data['bust_percent'] + 0.01)
total_data['td_rate'] = (total_data['passing_tds_avg'] + total_data['rushing_tds_avg'] + total_data['recieving_tds_avg'])
total_data['matchup_advantage'] = total_data['epa_per_play'] - total_data['avg_epa_against']
total_data['offensive_efficiency'] = total_data['epa_per_play'] * total_data['total_usage']
total_data['recent_volatility'] = abs(total_data['last_three_weeks_diff'])
total_data['boom_potential'] = total_data['boom_points_average'] - total_data['average_fantasy_points']
total_data['bust_risk'] = total_data['average_fantasy_points'] - total_data['bust_points_average']
total_data['variance_score'] = (total_data['boom_percent'] + total_data['bust_percent']) * total_data['average_fantasy_points']

total_data = pd.DataFrame([total_data])
feature_cols = [
    "bust_adjusted_avg", "recent_momentum", "boom_weighted_avg",
    "average_fantasy_points", "passing_target_percentage", "total_usage",
    "average_passing_yards", "points_against", "bust_points_average",
    "bust_percent", "boom_bust_ratio", "td_rate", "recieving_tds_avg",
    "boom_points_average", "rushing_tds_avg", "last_three_weeks_diff",
    "average_recieving_yards", "average_rushing_yards", "epa_per_play",
    "matchup_advantage", "offensive_efficiency", "boom_percent",
    "pass_epa_against", "rush_epa_against",
    "recent_volatility", "boom_potential", "bust_risk", "variance_score"
]

Week_features = data[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
Total_features = total_data[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)


with open('../models/fantasy_model2.pkl', 'rb') as f:
    model_data = pickle.load(f)
    xgb_model = model_data['model']

print(xgb_model.predict(Week_features))
