import pandas as pd 


def create_csvs(player_name, offensive_team_name, defensive_team_name, key): 
    # Load the csv
    pbp = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)

    # filter the dataframe
    offensive_team_data = pbp[(pbp['home_team'] == offensive_team_name) | (pbp['away_team'] == offensive_team_name)]

    # save to csv file
    offensive_team_output_path = f"../data/offensive_team{key}.csv"
    offensive_team_data.to_csv(offensive_team_output_path, index=False)
    print(f"Data saved to {offensive_team_output_path}")

    # filter for defense
    defensive_team_data = pbp[(pbp['home_team'] == defensive_team_name) | (pbp['away_team'] == defensive_team_name)]

    # save defense to csv file
    defensive_team_output_path = f"../data/defensive_team{key}.csv"
    defensive_team_data.to_csv(defensive_team_output_path, index=False)
    print(f"Data saved to {defensive_team_output_path}")

    # filter for player
    player_data = pbp[
        (pbp['passer_player_name'] == player_name) |
        (pbp['rusher_player_name'] == player_name) |
        (pbp['receiver_player_name'] == player_name)
    ]

    # Save to new csv   
    player_output_path = f"../data/player_data_{key}.csv"
    player_data.to_csv(player_output_path, index=False)
    print(f"Data saved to {player_output_path}")