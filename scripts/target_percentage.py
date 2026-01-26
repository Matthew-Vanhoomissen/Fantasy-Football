import pandas as pd


def get_percentage(team_name, player_name, pbp):
    percentage_data = []

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

    percentage_data.append({
        'player_name': player_name,
        'passing_target_percentage': percent,
        'rushing_percentage': percentR
    })

    return pd.DataFrame(percentage_data)


def get_week_percentage(team_name, player_name, pbp, week):
    percentage_data = []

    # Find target share percentage
    all_passing_plays = pbp[
        (pbp['posteam'] == team_name) &
        (pbp['play_type'] == "pass") &
        (pbp["pass_attempt"] == 1) &
        (pbp["sack"] == 0) &
        (pbp["qb_scramble"] == 0) &
        (pbp["penalty"] == 0) &
        (pbp['week'] < week)
        ]

    play_passing_plays = all_passing_plays[all_passing_plays['receiver_player_name'] == player_name]
    if len(all_passing_plays) == 0:
        percent = 0
    else:
        percent = len(play_passing_plays) / len(all_passing_plays)

    # Find carry percentage
    all_rushing_plays = pbp[
        (pbp['posteam'] == team_name) &
        (pbp['play_type'] == "run") &
        (pbp["rush_attempt"] == 1) &
        (pbp["sack"] == 0) &
        (pbp["qb_scramble"] == 0) &
        (pbp["penalty"] == 0) &
        (pbp['week'] < week)
        ]
    player_rushing_plays = all_rushing_plays[all_rushing_plays['rusher_player_name'] == player_name]
    if len(all_rushing_plays) == 0:
        percentR = 0
    else:
        percentR = len(player_rushing_plays) / len(all_rushing_plays)

    percentage_data.append({
        'week': week,
        'player_name': player_name,
        'passing_target_percentage': percent,
        'rushing_percentage': percentR
    })

    return pd.DataFrame(percentage_data)


    
