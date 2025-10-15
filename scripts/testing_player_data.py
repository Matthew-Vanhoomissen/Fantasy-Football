import pandas as pd


# Load the csv
pbp = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

# Search for a specific player
player_name = "T.Kraft"
team_name = "GB"

# Filter the dataframe
player_data = pbp[
    (pbp['passer_player_name'] == player_name) |
    (pbp['rusher_player_name'] == player_name) |
    (pbp['receiver_player_name'] == player_name)
]

# Find target share percentage
all_passing_plays = pbp[
    (pbp['posteam'] == team_name) &
    (pbp['play_type'] == "pass") &
    (pbp["pass_attempt"] == 1) &
    (pbp["sack"] == 0) &
    (pbp["qb_scramble"] == 0) &
    (pbp["penalty"] == 0)
    ]
play_passing_plays = all_passing_plays[all_passing_plays['receiver_player_name'] == player_name]
percent = len(play_passing_plays) / len(all_passing_plays)
print(f"Of all {len(all_passing_plays)} passing plays, the player was targeted {len(play_passing_plays)} time for a target percentage of {percent}")

# Find carry percentage
all_rushing_plays = pbp[
    (pbp['posteam'] == team_name) &
    (pbp['play_type'] == "run") &
    (pbp["rush_attempt"] == 1) &
    (pbp["sack"] == 0) &
    (pbp["qb_scramble"] == 0) &
    (pbp["penalty"] == 0)
    ]
player_rushing_plays = all_rushing_plays[all_rushing_plays['rusher_player_name'] == player_name]
percentR = len(player_rushing_plays) / len(all_rushing_plays)
print(f"Of all {len(all_rushing_plays)} rushing plays, the player was rushed {len(player_rushing_plays)} times for a carry percentage of {percentR}")

# Save to new csv
player_output_path = f"../data/player1_data_{2025}.csv"
player_data.to_csv(player_output_path, index=False)
print(f"Data saved to {player_output_path}")