import pandas as pd
import numpy as np
from itertools import combinations

data = pd.read_csv("../data/training_dataset_with_predictions.csv", low_memory=False)

pairs = []

for week in data['week'].unique():
    week_data = data[data['week'] == week]
    
    # Create pairs from all players in that week (regardless of position)
    # You can optionally limit this to avoid too many pairs
    player_indices = week_data.index.tolist()
    
    # Sample pairs if too many (optional - remove if you want all pairs)
    # if len(player_indices) > 50:
        # Randomly sample some pairs to keep dataset manageable
        # num_pairs = min(200, len(player_indices) * (len(player_indices) - 1) // 2)
        # sampled_pairs = []
        # for _ in range(num_pairs):
            # idx1, idx2 = np.random.choice(player_indices, 2, replace=False)
            # sampled_pairs.append((idx1, idx2))
    # else:
        # sampled_pairs = list(combinations(player_indices, 2))
    sampled_pairs = list(combinations(player_indices, 2))

    for player1_idx, player2_idx in sampled_pairs:
        p1 = week_data.loc[player1_idx]
        p2 = week_data.loc[player2_idx]
        
        # Features for comparison
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
            
            # Target: 1 if player1 scored more, 0 if player2 scored more
            'target': 1 if p1['week_fantasy_points'] > p2['week_fantasy_points'] else 0,
            
            # Store actual points for analysis (not used in training)
            'p1_actual_points': p1['week_fantasy_points'],
            'p2_actual_points': p2['week_fantasy_points']
        }
        
        pairs.append(pair_features)

pairs_df = pd.DataFrame(pairs)

pairs_df.to_csv("../data/player_pairs_dataset.csv", index=False)
print(f"✅ Created {len(pairs_df)} player comparison pairs")