import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import numpy as np
import pickle
import os

# Read and sort data by season to ensure there is no data leakage
data = pd.read_csv("data/training_dataset/training_dataset.csv", low_memory=False)
data = data.sort_values(['season', 'week']).reset_index(drop=True)

print(f"Total rows loaded: {len(data)}")
print(f"Seasons present: {data['season'].unique()}")
print(f"Weeks present: {data['week'].unique()}")
print(data.head())


# # === Feature Engineering ===
# data['bust_adjusted_avg'] = data['average_fantasy_points'] * (1 - data['bust_percent'])
# data['recent_momentum'] = data['average_fantasy_points'] + data['last_three_weeks_diff']
# data['boom_weighted_avg'] = data['average_fantasy_points'] * (1 + data['boom_percent'])
# data['total_usage'] = data['passing_target_percentage'] + data['rushing_percentage']
# data['boom_bust_ratio'] = data['boom_percent'] / (data['bust_percent'] + 0.01)
# data['td_rate'] = (data['passing_tds_avg'] + data['rushing_tds_avg'] + data['recieving_tds_avg'])
# data['matchup_advantage'] = data['epa_per_play'] - data['avg_epa_against']
# data['offensive_efficiency'] = data['epa_per_play'] * data['total_usage']

# # Add variance-capturing features
# data['recent_volatility'] = abs(data['last_three_weeks_diff'])
# data['boom_potential'] = data['boom_points_average'] - data['average_fantasy_points']
# data['bust_risk'] = data['average_fantasy_points'] - data['bust_points_average']
# data['variance_score'] = (data['boom_percent'] + data['bust_percent']) * data['average_fantasy_points']

# feature_cols = [
#     "bust_adjusted_avg", "recent_momentum", "boom_weighted_avg",
#     "average_fantasy_points", "passing_target_percentage", "total_usage",
#     "average_passing_yards", "points_against", "bust_points_average",
#     "bust_percent", "boom_bust_ratio", "td_rate", "recieving_tds_avg",
#     "boom_points_average", "rushing_tds_avg", "last_three_weeks_diff",
#     "average_recieving_yards", "average_rushing_yards", "epa_per_play",
#     "matchup_advantage", "offensive_efficiency", "boom_percent",
#     "pass_epa_against", "rush_epa_against",
#     # Variance features
#     "recent_volatility", "boom_potential", "bust_risk", "variance_score"
# ]
feature_cols = [
    "receptions_avg", "average_passing_yards", "average_rushing_yards",
    "average_recieving_yards", "passing_tds_avg", "rushing_tds_avg",
    "recieving_tds_avg", "average_fantasy_points", "bust_points_average",
    "bust_percent", "boom_points_average", "boom_percent", "last_three_weeks_diff",
    "passing_target_percentage", "rushing_percentage", "epa_per_play",
    "epa_per_rush", "epa_per_pass", "pass_percent", "rush_percent",
    "allowed_passing_yards", "allowed_rushing_yards", "sack_yards",
    "avg_epa_against", "pass_epa_against", "rush_epa_against", "points_against"
]

x = data[feature_cols]
y = data["week_fantasy_points"]

print(x.columns.tolist())

# Save for measuring how far to go each pass
time_index = data[['season', 'week']]


# Tune for capturing variance
model = XGBRegressor(
    n_estimators=700,
    learning_rate=0.015,      # Lower = captures nuances better
    max_depth=4,              # Deeper = more complex patterns
    min_child_weight=5,       # Lower = allows more splits
    subsample=0.85,
    colsample_bytree=0.75,
    gamma=1,                # Lower = less conservative
    reg_lambda=3.0,           # Less regularization
    reg_alpha=0.5,
    random_state=42,
    n_jobs=-1
)


unique_weeks = data[['season', 'week']].drop_duplicates().sort_values(['season', 'week']).reset_index(drop=True)

# Define how many weeks to test at a time
test_window = 3
min_train_weeks = 20  # minimum weeks before first test

fold_scores = []

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

    # Sanity check
    train_end = train_weeks.iloc[-1]
    test_start = test_weeks.iloc[0]
    print(f"Train ends S{train_end['season']} W{train_end['week']} "
          f"→ Test starts S{test_start['season']} W{test_start['week']}")

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    fold_r2 = r2_score(y_test, predictions)
    fold_scores.append(fold_r2)
    print(f"R²: {fold_r2:.4f}\n")


print(f"\nMean R²: {np.mean(fold_scores):.4f}")
print(f"Std R²:  {np.std(fold_scores):.4f}")


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
with open('models/fantasy_model_baseline.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("✅ Model saved to models/fantasy_model_baseline.pkl")
