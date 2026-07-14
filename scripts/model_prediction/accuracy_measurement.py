from itertools import combinations
import pandas as pd


def evaluate_pairwise_accuracy(output_df, min_predictions=True):
    """
    For each week, compare every pair of players and check if the model
    correctly predicted which one would score more.
    """
    # Only use rows where we have predictions
    predicted = output_df.dropna(subset=['predicted_fantasy_points']).copy()

    results = []

    weeks = predicted[['season', 'week']].drop_duplicates().sort_values(['season', 'week'])

    for _, week_row in weeks.iterrows():
        season, week = week_row['season'], week_row['week']

        week_data = predicted[
            (predicted['season'] == season) &
            (predicted['week'] == week)
        ].reset_index(drop=True)

        if len(week_data) < 2:
            continue

        correct = 0
        total = 0
        ties = 0

        for i, j in combinations(range(len(week_data)), 2):
            p1 = week_data.iloc[i]
            p2 = week_data.iloc[j]

            actual_winner = p1['player_name'] if p1['week_fantasy_points'] > p2['week_fantasy_points'] else p2['player_name']
            pred_winner = p1['player_name'] if p1['predicted_fantasy_points'] > p2['predicted_fantasy_points'] else p2['player_name']

            # Skip actual ties — no correct answer
            if p1['week_fantasy_points'] == p2['week_fantasy_points']:
                ties += 1
                continue

            if actual_winner == pred_winner:
                correct += 1
            total += 1

        if total > 0:
            week_accuracy = correct / total
            results.append({
                'season': season,
                'week': week,
                'correct': correct,
                'total': total,
                'ties_skipped': ties,
                'accuracy': week_accuracy
            })

    accuracy_df = pd.DataFrame(results)
    return accuracy_df


def evaluate_positional_pairwise(output_df):
    """
    Same as pairwise but only compares players of the same position.
    More representative of actual fantasy decisions.
    """
    predicted = output_df.dropna(subset=['predicted_fantasy_points']).copy()

    position_names = {0: 'QB', 1: 'RB', 2: 'WR_TE', 3: 'FLEX', -1: 'UNKNOWN'}
    results = []

    weeks = predicted[['season', 'week']].drop_duplicates().sort_values(['season', 'week'])

    for _, week_row in weeks.iterrows():
        season, week = week_row['season'], week_row['week']
        week_data = predicted[
            (predicted['season'] == season) &
            (predicted['week'] == week)
        ]

        for pos_code, pos_name in position_names.items():
            pos_data = week_data[week_data['position'] == pos_code].reset_index(drop=True)

            if len(pos_data) < 2:
                continue

            correct = 0
            total = 0

            for i, j in combinations(range(len(pos_data)), 2):
                p1 = pos_data.iloc[i]
                p2 = pos_data.iloc[j]

                if p1['week_fantasy_points'] == p2['week_fantasy_points']:
                    continue

                actual_winner = p1['player_name'] if p1['week_fantasy_points'] > p2['week_fantasy_points'] else p2['player_name']
                pred_winner = p1['player_name'] if p1['predicted_fantasy_points'] > p2['predicted_fantasy_points'] else p2['player_name']

                if actual_winner == pred_winner:
                    correct += 1
                total += 1

            if total > 0:
                results.append({
                    'season': season,
                    'week': week,
                    'position': pos_name,
                    'correct': correct,
                    'total': total,
                    'accuracy': correct / total
                })

    return pd.DataFrame(results)


output = pd.read_csv("data/training_dataset/predictions_output.csv", low_memory=False)

print("\n=== PAIRWISE RANKING ACCURACY ===")
pairwise_df = evaluate_pairwise_accuracy(output)

print(f"Weeks evaluated: {len(pairwise_df)}")
print(f"Total comparisons: {pairwise_df['total'].sum():,}")
print(f"Overall accuracy: {pairwise_df['correct'].sum() / pairwise_df['total'].sum():.4f}")
print(f"Mean weekly accuracy: {pairwise_df['accuracy'].mean():.4f}")
print(f"Std weekly accuracy:  {pairwise_df['accuracy'].std():.4f}")
print(f"Worst week:  S{pairwise_df.loc[pairwise_df['accuracy'].idxmin(), 'season']} "
      f"W{pairwise_df.loc[pairwise_df['accuracy'].idxmin(), 'week']} "
      f"→ {pairwise_df['accuracy'].min():.4f}")
print(f"Best week:   S{pairwise_df.loc[pairwise_df['accuracy'].idxmax(), 'season']} "
      f"W{pairwise_df.loc[pairwise_df['accuracy'].idxmax(), 'week']} "
      f"→ {pairwise_df['accuracy'].max():.4f}")

print("\n=== POSITIONAL PAIRWISE ACCURACY ===")
positional_df = evaluate_positional_pairwise(output)

positional_summary = positional_df.groupby('position').apply(
    lambda g: pd.Series({
        'total_comparisons': g['total'].sum(),
        'total_correct': g['correct'].sum(),
        'overall_accuracy': g['correct'].sum() / g['total'].sum(),
        'mean_weekly_accuracy': g['accuracy'].mean(),
        'std_weekly_accuracy': g['accuracy'].std()
    }), include_groups=False
).reset_index()

print(positional_summary.to_string(index=False))

# Export weekly accuracy for inspection
pairwise_df.to_csv("data/training_dataset/pairwise_accuracy.csv", index=False)
positional_df.to_csv("data/training_dataset/positional_accuracy.csv", index=False)
print("\nExported pairwise accuracy CSVs")
