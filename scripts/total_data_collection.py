import pandas as pd
import numpy as np
import pickle

from defensive_team_data import get_defensive_data
from finding_team_data import get_offensive_data
from player_stats_data import get_player_data
from make_csv import create_csvs_defense, create_csvs_offense


def get_player_input(player_name, offensive_team_name, defensive_team_name, all_data):
    
    defensive_team_data1 = create_csvs_defense(all_data, defensive_team_name)
    offensive_team_data1, player_data1 = create_csvs_offense(all_data, player_name, offensive_team_name)

    defensive_stats1 = get_defensive_data(defensive_team_name, defensive_team_data1)
    offensive_stats1 = get_offensive_data(offensive_team_name, offensive_team_data1)
    player_stats1 = get_player_data(player_name, offensive_team_name, player_data1, all_data)


    offensive_stats1 = offensive_stats1.rename(columns={"team_name": "off_team_name"})
    defensive_stats1 = defensive_stats1.rename(columns={"team_name": "def_team_name"})
    player_stats1 = player_stats1.rename(columns={"team_name": "off_team_name"})

    player_stats1["def_team_name"] = defensive_team_name

    data = (
        player_stats1
        .merge(offensive_stats1, on="off_team_name", how="left")
        .merge(defensive_stats1, how="left", left_on="def_team_name", right_on="def_team_name")
    )

    # === Feature Engineering ===
    data['bust_adjusted_avg'] = data['average_fantasy_points'] * (1 - data['bust_percent'])
    data['recent_momentum'] = data['average_fantasy_points'] + data['last_three_weeks_diff']
    data['boom_weighted_avg'] = data['average_fantasy_points'] * (1 + data['boom_percent'])
    data['total_usage'] = data['passing_target_percentage'] + data['rushing_percentage']
    data['boom_bust_ratio'] = data['boom_percent'] / (data['bust_percent'] + 0.01)
    data['td_rate'] = (data['passing_tds_avg'] + data['rushing_tds_avg'] + data['recieving_tds_avg'])
    data['matchup_advantage'] = data['epa_per_play'] - data['avg_epa_against']
    data['offensive_efficiency'] = data['epa_per_play'] * data['total_usage']

    # Add variance-capturing features
    data['recent_volatility'] = abs(data['last_three_weeks_diff'])
    data['boom_potential'] = data['boom_points_average'] - data['average_fantasy_points']
    data['bust_risk'] = data['average_fantasy_points'] - data['bust_points_average']
    data['variance_score'] = (data['boom_percent'] + data['bust_percent']) * data['average_fantasy_points']

    feature_cols = [
        "bust_adjusted_avg", "recent_momentum", "boom_weighted_avg",
        "average_fantasy_points", "passing_target_percentage", "total_usage",
        "average_passing_yards", "points_against", "bust_points_average",
        "bust_percent", "boom_bust_ratio", "td_rate", "recieving_tds_avg",
        "boom_points_average", "rushing_tds_avg", "last_three_weeks_diff",
        "average_recieving_yards", "average_rushing_yards", "epa_per_play",
        "matchup_advantage", "offensive_efficiency", "boom_percent",
        "pass_epa_against", "rush_epa_against",
        # Variance features
        "recent_volatility", "boom_potential", "bust_risk", "variance_score"
    ]

    with open('../models/fantasy_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
        xgb_model = model_data['model']

    x = data[feature_cols]
    x = x.replace([np.inf, -np.inf], np.nan).fillna(0)

    projection = xgb_model.predict(x)
    
    data['xgb_predicted_points'] = projection

    return data.iloc[0].to_dict()


def create_pair_input(player1, player1_team, player1_defense, player2, player2_team, player2_defense):
    all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

    p1 = get_player_input(player1, player1_team, player1_defense, all_data)
    p2 = get_player_input(player2, player2_team, player2_defense, all_data)
    pair = []

    pair_features = {
            # Player 1 features
            'p1_xgb_pred': p1['xgb_predicted_points'],
            'p1_avg_points': p1['average_fantasy_points'],
            'p1_recent_momentum': p1['recent_momentum'],
            'p1_boom_percent': p1['boom_percent'],
            'p1_bust_percent': p1['bust_percent'],
            'p1_usage': p1['total_usage'],
            'p1_matchup': p1['matchup_advantage'],
            'p1_variance': p1['variance_score'],
            'p1_boom_potential': p1['boom_potential'],
            'p1_bust_risk': p1['bust_risk'],
            
            # Player 2 features
            'p2_xgb_pred': p2['xgb_predicted_points'],
            'p2_avg_points': p2['average_fantasy_points'],
            'p2_recent_momentum': p2['recent_momentum'],
            'p2_boom_percent': p2['boom_percent'],
            'p2_bust_percent': p2['bust_percent'],
            'p2_usage': p2['total_usage'],
            'p2_matchup': p2['matchup_advantage'],
            'p2_variance': p2['variance_score'],
            'p2_boom_potential': p2['boom_potential'],
            'p2_bust_risk': p2['bust_risk'],
            
            # Differential features (most important for decision)
            'pred_diff': p1['xgb_predicted_points'] - p2['xgb_predicted_points'],
            'avg_diff': p1['average_fantasy_points'] - p2['average_fantasy_points'],
            'momentum_diff': p1['recent_momentum'] - p2['recent_momentum'],
            'boom_diff': p1['boom_percent'] - p2['boom_percent'],
            'usage_diff': p1['total_usage'] - p2['total_usage'],
            'matchup_diff': p1['matchup_advantage'] - p2['matchup_advantage'],
            'variance_diff': p1['variance_score'] - p2['variance_score'],
            
            # Ratio features
            'pred_ratio': p1['xgb_predicted_points'] / (p2['xgb_predicted_points'] + 0.1) if p2['xgb_predicted_points'] >= 0 else p1['xgb_predicted_points'] / (p2['xgb_predicted_points']),
            'avg_ratio': p1['average_fantasy_points'] / (p2['average_fantasy_points'] + 0.1) if p2['average_fantasy_points'] >= 0 else p1['average_fantasy_points'] / (p2['average_fantasy_points']),
        }
    pair.append(pair_features)

    return pair
    
