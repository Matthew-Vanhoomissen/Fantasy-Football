import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import numpy as np
import pickle
import os

# Read and sort data by season to ensure there is no data leakage
data = pd.read_csv("data/training_dataset/training_dataset.csv", low_memory=False)
data = data.sort_values(['season', 'week']).reset_index(drop=True)

# data['recent_momentum'] = data['last_three_weeks_diff'] / (data['average_fantasy_points'] + .01)


feature_cols = [
    "receptions_avg", "average_passing_yards", "average_rushing_yards",
    "average_recieving_yards", "passing_tds_avg", "rushing_tds_avg",
    "recieving_tds_avg", "bust_points_average",
    "bust_percent", "boom_points_average", "boom_percent",
    "passing_target_percentage", "rushing_percentage",
    "epa_per_rush", "epa_per_pass", "pass_percent", "rush_percent",
    "allowed_passing_yards", "allowed_rushing_yards", "sack_yards",
    "pass_epa_against", "rush_epa_against", "points_against",
    "position", "redzone_carries", "redzone_targets"
]

# Residual target — what we're now predicting
data['points_above_average'] = data['week_fantasy_points'] - data['average_fantasy_points']

# Sanity check on residual distribution before training
print("=== Residual Target Distribution ===")
print(data['points_above_average'].describe())
print(f"Std of residuals: {data['points_above_average'].std():.2f}")
print(f"Predictions near zero (within 1pt): {(data['points_above_average'].abs() < 1).sum()}")
print()

x = data[feature_cols]
y = data['points_above_average']

time_index = data[['season', 'week']]

# Slightly loosened regularization for residual modeling
# residuals are harder to predict so we give the model more freedom
model = XGBRegressor(
    n_estimators=700,
    learning_rate=0.01,
    max_depth=4,
    min_child_weight=3,    # loosened from 4
    subsample=0.85,
    colsample_bytree=0.75,
    gamma=0.5,             # loosened from 1
    reg_lambda=2.0,        # loosened from 3.0
    reg_alpha=0.3,         # loosened from 0.5
    random_state=42,
    n_jobs=-1
)

# Store both residual prediction and final reconstructed points
data['predicted_deviation'] = np.nan
data['predicted_fantasy_points'] = np.nan

unique_weeks = (data[['season', 'week']]
    .drop_duplicates()
    .sort_values(['season', 'week'])
    .reset_index(drop=True))

test_window = 3
min_train_weeks = 20

fold_scores = []
fold_scores_raw = []  # R² on actual fantasy points for comparison

for i in range(min_train_weeks, len(unique_weeks) - test_window + 1, test_window):
    train_weeks = unique_weeks.iloc[:i]
    test_weeks = unique_weeks.iloc[i:i + test_window]

    train_mask = data.set_index(['season', 'week']).index.isin(
        [tuple(r) for r in train_weeks.values]
    )
    test_mask = data.set_index(['season', 'week']).index.isin(
        [tuple(r) for r in test_weeks.values]
    )

    x_train, x_test = x[train_mask], x[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    train_end = train_weeks.iloc[-1]
    test_start = test_weeks.iloc[0]
    print(f"Train ends S{train_end['season']} W{train_end['week']} "
          f"→ Test starts S{test_start['season']} W{test_start['week']}")

    model.fit(x_train, y_train)

    # Predict the deviation from average
    predicted_deviation = model.predict(x_test)

    # Reconstruct actual fantasy points by adding average back
    test_averages = data.loc[test_mask, 'average_fantasy_points'].values
    predicted_raw_points = predicted_deviation + test_averages

    # Store both
    data.loc[test_mask, 'predicted_deviation'] = predicted_deviation
    data.loc[test_mask, 'predicted_fantasy_points'] = predicted_raw_points

    # R² on residuals — what the model is actually learning
    fold_r2 = r2_score(y_test, predicted_deviation)
    fold_scores.append(fold_r2)

    # R² on reconstructed raw points — comparable to your previous runs
    actual_raw_points = data.loc[test_mask, 'week_fantasy_points'].values
    fold_r2_raw = r2_score(actual_raw_points, predicted_raw_points)
    fold_scores_raw.append(fold_r2_raw)

    print(f"R² (residual):     {fold_r2:.4f}")
    print(f"R² (reconstructed): {fold_r2_raw:.4f}\n")

print(f"Mean R² (residual):      {np.mean(fold_scores):.4f}")
print(f"Std R²  (residual):      {np.std(fold_scores):.4f}")
print(f"Mean R² (reconstructed): {np.mean(fold_scores_raw):.4f}")
print(f"Std R²  (reconstructed): {np.std(fold_scores_raw):.4f}")

output = data[['player_name', 'season', 'week', 'week_fantasy_points',
               'average_fantasy_points', 'predicted_deviation',
               'predicted_fantasy_points', 'position']].copy()

output.to_csv("data/training_dataset/predictions_output.csv", index=False)

# Feature importance
importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(importance.head(10))


# Save the model and necessary components
model_data = {
    'model': model,
    'feature_cols': feature_cols,
    'scaler_mean': x_train.mean(),
    'scaler_std': x_train.std()
}

# Create models directory if it doesn't exist

os.makedirs("models", exist_ok=True)

# Save to file
with open('models/fantasy_model_deviation.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("✅ Model saved to models/fantasy_model_deviation.pkl")
