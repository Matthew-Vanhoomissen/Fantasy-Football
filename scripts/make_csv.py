import pandas as pd 


def create_csvs_offense(pbp, player_name, offensive_team_name, key):

    # filter the dataframe
    offensive_team_data = pbp[(pbp['home_team'] == offensive_team_name) | (pbp['away_team'] == offensive_team_name)]

    # filter for player
    player_data = pbp[
        (pbp['passer_player_name'] == player_name) |
        (pbp['rusher_player_name'] == player_name) |
        (pbp['receiver_player_name'] == player_name)
    ]

    return offensive_team_data, player_data


def create_csvs_defense(pbp, defense_team_name):

    # filter for defense
    defensive_team_data = pbp[(pbp['home_team'] == defense_team_name) | (pbp['away_team'] == defense_team_name)]

    return defensive_team_data
