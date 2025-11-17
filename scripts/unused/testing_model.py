import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader

# Load the pairs data (same data used for training/testing)
pairs_df = pd.read_csv("../data/player_pairs_dataset.csv")

# Separate features from target
feature_cols = [col for col in pairs_df.columns if col not in ['target', 'p1_actual_points', 'p2_actual_points']]
X = pairs_df[feature_cols].values
y = pairs_df['target'].values

# Get actual points for filtering
p1_actual = pairs_df['p1_actual_points'].values
p2_actual = pairs_df['p2_actual_points'].values

# Calculate point difference between players
point_diff = np.abs(p1_actual - p2_actual)

# Define closeness thresholds to test
thresholds = [
    (0, 2, "Very Close (0-2 points)"),
    (0, 3, "Close (0-3 points)"),
    (0, 5, "Moderate (0-5 points)"),
    (3, 7, "Medium (3-7 points)"),
    (5, 10, "Standard (5-10 points)"),
    (10, float('inf'), "Wide Gap (10+ points)")
]

# Load the trained model checkpoint
checkpoint = torch.load('../models/start_sit_model.pth', weights_only=False)
scaler = checkpoint['scaler']  # Get the scaler used during training


# Define model architecture (must match training)
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


# Recreate and load the trained model
model = StartSitModel(checkpoint['input_size'])
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()  # Set to evaluation mode

print("=== Model Accuracy by Matchup Closeness ===\n")


# Custom Dataset class (same as training)
class SimpleDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# Test on different closeness thresholds
for min_diff, max_diff, label in thresholds:
    # Filter pairs within this threshold range
    mask = (point_diff >= min_diff) & (point_diff < max_diff)
    X_subset = X[mask]
    y_subset = y[mask]
    
    # Skip if not enough samples to test
    if len(X_subset) < 10:
        print(f"{label}: Not enough samples ({len(X_subset)})\n")
        continue
    
    # Scale features using the same scaler from training
    X_scaled = scaler.transform(X_subset)
    
    # Convert to PyTorch tensors
    X_tensor = torch.FloatTensor(X_scaled)
    y_tensor = torch.FloatTensor(y_subset).unsqueeze(1)
    
    # Create dataloader for batched processing
    test_dataset = SimpleDataset(X_tensor, y_tensor)
    test_loader = DataLoader(test_dataset, batch_size=512, shuffle=False)
    
    # Evaluate model on this subset
    correct = 0
    total = 0
    confidences = []
    
    # No gradient calculation needed for evaluation
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch)  # Get probability predictions
            predicted = (outputs > 0.5).float()  # Convert to binary (0 or 1)
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()
            confidences.extend(outputs.squeeze().tolist())  # Store confidence scores
    
    # Calculate metrics
    accuracy = 100 * correct / total
    avg_confidence = np.mean(confidences)
    
    print(f"{label}:")
    print(f"  Samples: {total:,}")
    print(f"  Accuracy: {accuracy:.2f}%")
    print(f"  Avg Confidence: {avg_confidence:.3f}")
    print(f"  Baseline (random guess): 50.00%")
    print(f"  Improvement over baseline: +{accuracy - 50:.2f}%\n")

# Additional analysis: Accuracy by XGBoost prediction difference
print("\n=== Accuracy by XGBoost Prediction Gap ===\n")

# Get the prediction difference feature (how far apart XGBoost thinks they are)
xgb_pred_diff = np.abs(pairs_df['pred_diff'].values)

pred_thresholds = [
    (0, 2, "XGB Very Close (0-2)"),
    (2, 5, "XGB Close (2-5)"),
    (5, 10, "XGB Medium (5-10)"),
    (10, float('inf'), "XGB Wide (10+)")
]

for min_diff, max_diff, label in pred_thresholds:
    mask = (xgb_pred_diff >= min_diff) & (xgb_pred_diff < max_diff)
    X_subset = X[mask]
    y_subset = y[mask]
    
    if len(X_subset) < 10:
        print(f"{label}: Not enough samples ({len(X_subset)})\n")
        continue
    
    X_scaled = scaler.transform(X_subset)
    X_tensor = torch.FloatTensor(X_scaled)
    y_tensor = torch.FloatTensor(y_subset).unsqueeze(1)
    
    test_dataset = SimpleDataset(X_tensor, y_tensor)
    test_loader = DataLoader(test_dataset, batch_size=512, shuffle=False)
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch)
            predicted = (outputs > 0.5).float()
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()
    
    accuracy = 100 * correct / total
    
    print(f"{label}:")
    print(f"  Samples: {total:,}")
    print(f"  Accuracy: {accuracy:.2f}%")
    print(f"  Improvement over baseline: +{accuracy - 50:.2f}%\n")

# Find the hardest cases (where model is confident but wrong)
print("\n=== Hardest Cases (High Confidence Incorrect Predictions) ===\n")

# Get predictions and confidences for entire dataset
X_scaled_all = scaler.transform(X)
X_tensor_all = torch.FloatTensor(X_scaled_all)

with torch.no_grad():
    all_outputs = model(X_tensor_all)
    all_predictions = (all_outputs > 0.5).float().squeeze()
    all_confidences = all_outputs.squeeze()

# Find incorrect predictions
incorrect_mask = (all_predictions != torch.FloatTensor(y))
incorrect_indices = np.where(incorrect_mask.numpy())[0]

if len(incorrect_indices) > 0:
    # Get details for incorrect predictions
    incorrect_confidences = all_confidences[incorrect_indices].numpy()
    incorrect_point_diffs = point_diff[incorrect_indices]
    
    # Sort by confidence distance from 0.5 (most confident mistakes first)
    confidence_distance = np.abs(incorrect_confidences - 0.5)
    sorted_indices = np.argsort(-confidence_distance)[:10]
    
    print("Top 10 most confident incorrect predictions:")
    for i, idx in enumerate(sorted_indices, 1):
        orig_idx = incorrect_indices[idx]
        conf = incorrect_confidences[idx]
        point_diff_val = incorrect_point_diffs[idx]
        p1_pts = p1_actual[orig_idx]
        p2_pts = p2_actual[orig_idx]
        
        # Calculate actual confidence (0.5 to 1.0 range)
        actual_confidence = abs(conf - 0.5) + 0.5
        
        print(f"{i}. Confidence: {actual_confidence:.3f}, "
              f"Actual point diff: {point_diff_val:.1f} pts "
              f"(Player 1: {p1_pts:.1f}, Player 2: {p2_pts:.1f})")

print("\n✅ Analysis complete!")