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
    "recieving_tds_avg", "bust_points_average",  # "average_fantasy_points",
    "bust_percent", "boom_points_average", "boom_percent", # "recent_momentum",
    "passing_target_percentage", "rushing_percentage",
    "epa_per_rush", "epa_per_pass", "pass_percent", "rush_percent",
    "allowed_passing_yards", "allowed_rushing_yards", "sack_yards",
    "pass_epa_against", "rush_epa_against", "points_against",
    "position"
]

data['points_above_average'] = data['week_fantasy_points'] - data['average_fantasy_points']

x = data[feature_cols]
y = data['points_above_average']

# Save for measuring how far to go each pass
time_index = data[['season', 'week']]


# Tune for capturing variance
model = XGBRegressor(
    n_estimators=700,
    learning_rate=0.01,      # Lower = captures nuances better
    max_depth=4,              # Deeper = more complex patterns
    min_child_weight=4,       # Lower = allows more splits
    subsample=0.85,
    colsample_bytree=0.75,
    gamma=1,                # Lower = less conservative
    reg_lambda=3.0,           # Less regularization
    reg_alpha=0.5,
    random_state=42,
    n_jobs=-1
)

data['predicted_fantasy_points'] = np.nan

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

    data.loc[test_mask, 'predicted_fantasy_points'] = predictions

    fold_r2 = r2_score(y_test, predictions)
    fold_scores.append(fold_r2)
    print(f"R²: {fold_r2:.4f}\n")


print(f"\nMean R²: {np.mean(fold_scores):.4f}")
print(f"Std R²:  {np.std(fold_scores):.4f}")


output = data[['player_name', 'season', 'week', 'week_fantasy_points',
               'predicted_fantasy_points', 'average_fantasy_points', 'position']]

output.to_csv("data/training_dataset/predictions_output.csv", index=False)
print(f"Exported {len(output)} rows")

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
