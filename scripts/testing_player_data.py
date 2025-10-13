import pandas as pd


# Load the csv
pbp = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

# Search for a specific player
player_name = "T.Kraft"

# Filter the dataframe
player_data = pbp[
    (pbp['passer_player_name'] == player_name) |
    (pbp['rusher_player_name'] == player_name) |
    (pbp['receiver_player_name'] == player_name)
]

# Save to new csv
player_output_path = f"../data/player1_data_{2025}.csv"
player_data.to_csv(player_output_path, index=False)
print(f"Data saved to {player_output_path}")