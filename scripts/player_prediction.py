from total_data_collection import create_pair_input


import pandas as pd 
import torch.nn as nn
import numpy as np
import torch


class StartSitModel(nn.Module):
    def __init__(self, input_size):
        super(StartSitModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.25),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)
    

def predict_start_sit(pair_df):
    """
    Make start/sit prediction given a dataframe with comparison features
    
    Args:
        pair_df: DataFrame with one row containing all comparison features
                 Expected columns: p1_xgb_pred, p1_avg_points, p1_recent_momentum,
                                  p1_boom_percent, p1_bust_percent, p1_usage,
                                  p1_matchup, p1_variance, p1_boom_potential,
                                  p1_bust_risk, p2_xgb_pred, p2_avg_points,
                                  p2_recent_momentum, p2_boom_percent, p2_bust_percent,
                                  p2_usage, p2_matchup, p2_variance, p2_boom_potential,
                                  p2_bust_risk, pred_diff, avg_diff, momentum_diff,
                                  boom_diff, usage_diff, matchup_diff, variance_diff,
                                  pred_ratio, avg_ratio
    
    Returns:
        Dictionary with recommendation and confidence
    """
    
    # Load PyTorch model
    checkpoint = torch.load('../models/start_sit_model.pth', weights_only=False)
    pytorch_model = StartSitModel(checkpoint['input_size'])
    pytorch_model.load_state_dict(checkpoint['model_state_dict'])
    pytorch_model.eval()
    scaler = checkpoint['scaler']
    
    # Define feature columns in correct order
    feature_cols = [
        'p1_xgb_pred', 'p1_avg_points', 'p1_recent_momentum',
        'p1_boom_percent', 'p1_bust_percent', 'p1_usage',
        'p1_matchup', 'p1_variance', 'p1_boom_potential', 'p1_bust_risk',
        'p2_xgb_pred', 'p2_avg_points', 'p2_recent_momentum',
        'p2_boom_percent', 'p2_bust_percent', 'p2_usage',
        'p2_matchup', 'p2_variance', 'p2_boom_potential', 'p2_bust_risk',
        'pred_diff', 'avg_diff', 'momentum_diff', 'boom_diff',
        'usage_diff', 'matchup_diff', 'variance_diff',
        'pred_ratio', 'avg_ratio'
    ]
    
    # Extract features from dataframe
    X = pair_df[feature_cols].values
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Convert to tensor
    X_tensor = torch.FloatTensor(X_scaled)
    
    # Get prediction
    with torch.no_grad():
        output = pytorch_model(X_tensor)
        confidence = output.item()
    
    # Determine recommendation
    if confidence > 0.5:
        recommended_player = 1
        confidence_pct = confidence * 100
    else:
        recommended_player = 2
        confidence_pct = (1 - confidence) * 100
    
    # Return results
    result = {
        'recommended_player': recommended_player,  # 1 or 2
        'confidence': confidence_pct,
        'raw_confidence': confidence,  # 0-1 value
        'player1_projected': pair_df['p1_xgb_pred'].iloc[0],
        'player2_projected': pair_df['p2_xgb_pred'].iloc[0]
    }
    
    return result


if __name__ == "__main__":
    p1 = "J.Addison"
    p1_t = "MIN"
    p1_d = "GB"

    p2 = "K.Shakir"
    p2_t = "BUF"
    p2_d = "HOU"

    week = 11
    pair_data = create_pair_input(p1, p1_t, p1_d, p2, p2_t, p2_d, week)
    pair_data = pd.DataFrame(pair_data)
    result = predict_start_sit(pair_data)
    print(result)
