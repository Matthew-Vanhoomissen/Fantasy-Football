import pandas as pd


def return_opponent(team, week, season):
    schedule = pd.read_csv(f"data/schedule_{season}.csv")

    schedule = schedule[schedule["week"] == week]

    away = schedule[schedule['away_team'] == team]
    if not away.empty:
        return (away.iloc[0])['home_team']
    home = schedule[schedule['home_team'] == team]
    if not home.empty:
        return (home.iloc[0])['away_team']

    return None
