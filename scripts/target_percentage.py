import pandas as pd


def get_percentage(team_name, player_name):
    # load csv
    pbp = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

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



    
