import pandas as pd
import numpy as np
import pickle
from xgboost import XGBRegressor

# Load your trained XGBoost model
with open('../models/fantasy_model.pkl', 'rb') as f:
    model_data = pickle.load(f)
    xgb_model = model_data['model']

# Load your training data
data = pd.read_csv("../data/training_dataset.csv", low_memory=False)

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

# Get XGBoost predictions
X_features = data[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
data['xgb_predicted_points'] = xgb_model.predict(X_features)

# Save
data.to_csv("../data/training_dataset_with_predictions.csv", index=False)
print("✅ Saved dataset with XGBoost predictions")