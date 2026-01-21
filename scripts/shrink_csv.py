import pandas as pd 

NEEDED_COLUMNS = [
    'week',
    'posteam',
    'defteam',
    'passer_player_name',
    'rusher_player_name',
    'receiver_player_name',
    'fumbled_1_player_name',
    'play_type',
    'kickoff_attempt',
    'extra_point_attempt',
    'qb_kneel',
    'qb_spike',
    'penalty',
    'two_point_attempt',
    'pass_attempt',
    'rush_attempt',
    'sack',
    'qb_scramble',
    'passing_yards',
    'rushing_yards',
    'receiving_yards',
    'yards_gained',
    'complete_pass',
    'interception',
    'fumble_lost',
    'pass_touchdown',
    'rush_touchdown',
    'two_point_conv_result',
    'epa',
    'td_team',
    'touchdown',
    'field_goal_result',
    'extra_point_result',
    'penalty_team',
    'penalty_yards',
    'home_team',
    'away_team'
]

all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False, dtype={'week': 'int8', 'season': 'int16'}, usecols=NEEDED_COLUMNS)

all_data.to_csv("../data/play_by_play_2025.csv", index=False)