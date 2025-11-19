import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import numpy as np
import pickle
import os

data = pd.read_csv("../data/training_dataset.csv", low_memory=False)

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

x = data[feature_cols]
y = data["week_fantasy_points"]

x = x.replace([np.inf, -np.inf], np.nan).fillna(0)

# Less aggressive outlier removal to preserve variance
q1 = y.quantile(0.01)
q99 = y.quantile(0.99)
mask = (y >= q1) & (y <= q99)
x = x[mask]
y = y[mask]
print(f"Training samples: {len(y)}")

x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=.2, random_state=42
)

# Tune for capturing variance
model = XGBRegressor(
    n_estimators=700,
    learning_rate=0.015,      # Lower = captures nuances better
    max_depth=9,              # Deeper = more complex patterns
    min_child_weight=2,       # Lower = allows more splits
    subsample=0.85,
    colsample_bytree=0.75,
    gamma=0.1,                # Lower = less conservative
    reg_lambda=2.0,           # Less regularization
    reg_alpha=0.5,
    random_state=42,
    n_jobs=-1
)

model.fit(x_train, y_train)
preds = model.predict(x_test)

mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"Mean Absolute Error: {mae:.3f}")
print(f"R^2 Score: {r2:.3f}")

print("\nPrediction Analysis:")
print(f"Actual mean: {y_test.mean():.2f}, std: {y_test.std():.2f}")
print(f"Predicted mean: {preds.mean():.2f}, std: {preds.std():.2f}")

# Analyze prediction errors
errors = y_test - preds
print(f"\nError Analysis:")
print(f"Mean error: {errors.mean():.3f}")
print(f"Error std: {errors.std():.3f}")
print(f"Predictions within 3 points: {(abs(errors) <= 3).sum() / len(errors) * 100:.1f}%")
print(f"Predictions within 5 points: {(abs(errors) <= 5).sum() / len(errors) * 100:.1f}%")

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

os.makedirs("../models", exist_ok=True)

# Save to file
with open('../models/fantasy_model.pkl2', 'wb') as f:
    pickle.dump(model_data, f)

print("✅ Model saved to ../models/fantasy_model2.pkl")
