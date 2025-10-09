import pandas as pd

# Load the csv
pbp = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

# selected team
team_name = "GB"

# filter the dataframe
team_data = pbp[(pbp['home_team'] == team_name) | (pbp['away_team'] == team_name)]

# save to csv file
team_output_path = f"../data/team_data_{2025}.csv"
team_data.to_csv(team_output_path, index=False)
print(f"Data saved to {team_output_path}")