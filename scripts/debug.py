import pandas as pd
import numpy as np

data = pd.read_csv("../data/training_dataset.csv", low_memory=False)

# Feature engineering
data['bust_adjusted_avg'] = data['average_fantasy_points'] * (1 - data['bust_percent'])
data['recent_momentum'] = data['average_fantasy_points'] + data['last_three_weeks_diff']
data['boom_weighted_avg'] = data['average_fantasy_points'] * (1 + data['boom_percent'])
data['total_usage'] = data['passing_target_percentage'] + data['rushing_percentage']
data['boom_bust_ratio'] = data['boom_percent'] / (data['bust_percent'] + 0.01)
data['td_rate'] = (data['passing_tds_avg'] + data['rushing_tds_avg'] + data['recieving_tds_avg'])
data['matchup_advantage'] = data['epa_per_play'] - data['avg_epa_against']
data['offensive_efficiency'] = data['epa_per_play'] * data['total_usage']

# Check feature ranges by season
print("2024 Feature Ranges:")
data_2024 = data[data['season'] == 2024]
print(f"recent_momentum: min={data_2024['recent_momentum'].min():.2f}, max={data_2024['recent_momentum'].max():.2f}, mean={data_2024['recent_momentum'].mean():.2f}")
print(f"epa_per_play: min={data_2024['epa_per_play'].min():.2f}, max={data_2024['epa_per_play'].max():.2f}, mean={data_2024['epa_per_play'].mean():.2f}")
print(f"matchup_advantage: min={data_2024['matchup_advantage'].min():.2f}, max={data_2024['matchup_advantage'].max():.2f}, mean={data_2024['matchup_advantage'].mean():.2f}")

print("\n2025 Feature Ranges:")
data_2025 = data[data['season'] == 2025]
print(f"recent_momentum: min={data_2025['recent_momentum'].min():.2f}, max={data_2025['recent_momentum'].max():.2f}, mean={data_2025['recent_momentum'].mean():.2f}")
print(f"epa_per_play: min={data_2025['epa_per_play'].min():.2f}, max={data_2025['epa_per_play'].max():.2f}, mean={data_2025['epa_per_play'].mean():.2f}")
print(f"matchup_advantage: min={data_2025['matchup_advantage'].min():.2f}, max={data_2025['matchup_advantage'].max():.2f}, mean={data_2025['matchup_advantage'].mean():.2f}")

print(f"\n2024 rows: {len(data_2024)}")
print(f"2025 rows: {len(data_2025)}")

# Check how many weeks of 2025 data you have
print(f"\n2025 weeks in training data: {sorted(data_2025['week'].unique())}")