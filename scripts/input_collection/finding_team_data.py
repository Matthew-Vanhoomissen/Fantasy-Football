import pandas as pd


def get_offensive_data(team_name, team_data): 
    offensive_stats = []

    # all offensive plays
    offensive_plays = team_data[
        (team_data['posteam'] == team_name) & 
        (team_data['play_type'].isin(['pass', 'run'])) &
        (team_data['kickoff_attempt'] == 0) &
        (team_data['extra_point_attempt'] == 0) &
        (team_data['epa'].notna()) &
        (team_data['qb_kneel'] == 0) &
        (team_data['qb_spike'] == 0) &
        (team_data['penalty'] == 0) & 
        (team_data['two_point_attempt'] == 0)
    ]

    # average, total, rush, and passing epa

    total_epa = offensive_plays['epa'].sum()
    total_plays = len(offensive_plays)
    epa_per_play = total_epa / total_plays

    pass_plays = offensive_plays[
        (offensive_plays['play_type'] == 'pass')
    ]

    total_pass_epa = pass_plays['epa'].sum()
    total_pass_plays = len(pass_plays)
    epa_per_pass = total_pass_epa / total_pass_plays

    run_plays = offensive_plays[
        (offensive_plays['play_type'] == 'run')
    ]

    total_rush_epa = run_plays['epa'].sum()
    total_rush_plays = len(run_plays)
    epa_per_rush = total_rush_epa / total_rush_plays

    # Play type percentage
    all_plays = team_data[
        (team_data['posteam'] == team_name) &
        (team_data['play_type'].isin(['pass', 'run']))
    ]

    all_num_plays = len(all_plays)
    all_pass_plays = len(all_plays[all_plays['play_type'] == 'pass'])
    all_rush_plays = len(all_plays[all_plays['play_type'] == 'run'])

    pass_percent = (all_pass_plays / all_num_plays) * 100
    rush_percent = (all_rush_plays / all_num_plays) * 100

    offensive_stats.append({
        'team_name': team_name,
        'epa_per_play': epa_per_play,
        'epa_per_rush': epa_per_rush,
        'epa_per_pass': epa_per_pass,
        'pass_percent': pass_percent,
        'rush_percent': rush_percent
        
    })

    return pd.DataFrame(offensive_stats)


def get_offensive_week_data(team_name, team_data, week): 
    # Make empty array
    offensive_stats = []

    # all offensive plays
    offensive_plays = team_data[
        (team_data['posteam'] == team_name) & 
        (team_data['play_type'].isin(['pass', 'run'])) &
        (team_data['kickoff_attempt'] == 0) &
        (team_data['extra_point_attempt'] == 0) &
        (team_data['epa'].notna()) &
        (team_data['qb_kneel'] == 0) &
        (team_data['qb_spike'] == 0) &
        (team_data['penalty'] == 0) & 
        (team_data['two_point_attempt'] == 0) &
        (team_data['week'] < week)
    ]
    if len(offensive_plays) == 0:
        print("DING DING")
        return None

    # average, total, rush, and passing epa

    total_epa = offensive_plays['epa'].sum()
    total_plays = len(offensive_plays)
    epa_per_play = total_epa / total_plays

    pass_plays = offensive_plays[
        (offensive_plays['play_type'] == 'pass') 
    ]

    total_pass_epa = pass_plays['epa'].sum()
    total_pass_plays = len(pass_plays)
    epa_per_pass = total_pass_epa / total_pass_plays

    run_plays = offensive_plays[
        (offensive_plays['play_type'] == 'run')
    ]

    total_rush_epa = run_plays['epa'].sum()
    total_rush_plays = len(run_plays)
    epa_per_rush = total_rush_epa / total_rush_plays

    # Play type percentage
    all_plays = team_data[
        (team_data['posteam'] == team_name) &
        (team_data['play_type'].isin(['pass', 'run'])) & 
        (team_data['week'] < week)
    ]

    all_num_plays = len(all_plays)
    all_pass_plays = len(all_plays[all_plays['play_type'] == 'pass'])
    all_rush_plays = len(all_plays[all_plays['play_type'] == 'run'])

    pass_percent = (all_pass_plays / all_num_plays) * 100
    rush_percent = (all_rush_plays / all_num_plays) * 100

    # Third and Fourth down conversion rate
    all_third_downs = len(all_plays[all_plays['down'] == 3.0])
    all_fourth_downs = len(all_plays[all_plays['down'] == 4.0])

    converted_third_downs = len(all_plays[all_plays['third_down_converted'] == 1.0])
    converted_fourth_downs = len(all_plays[all_plays['fourth_down_converted'] == 1.0])

    third_down_completion = converted_third_downs / all_third_downs if all_third_downs > 0 else 0
    fourth_down_completion = converted_fourth_downs / all_fourth_downs if all_fourth_downs > 0 else 0

    # Percentage of drives the team scores/success rate
    total_drives = all_plays.groupby('week')['down'].nunique().sum()

    # Filter for scoring plays
    successful_drives_df = all_plays[(all_plays['touchdown'] == 1) | (all_plays['field_goal_result'] == "made")]

    # Count unique successful combinations of week and drive
    successful_drives = successful_drives_df.groupby('week')['down'].nunique().sum()

    success_rate = successful_drives / total_drives if total_drives > 0 else 0

    # Home or away
    home_team = 1 if all_plays.iloc[0]['home_team'] == team_name else 0

    offensive_stats.append({
        'week': week,
        'team_name': team_name,
        'epa_per_play': epa_per_play,
        'epa_per_rush': epa_per_rush,
        'epa_per_pass': epa_per_pass,
        'pass_percent': pass_percent,
        'rush_percent': rush_percent,
        'third_down_completion': third_down_completion,
        'fourth_down_completion': fourth_down_completion,
        'success_rate': success_rate,
        'home_team': home_team
    })

    return pd.DataFrame(offensive_stats)

# TODO
# Possible new inputs: vegas odds, offensive team 3rd and 4th down conversions, defensive conversion allow rate,
# completion percentage + advnaced cpoe, possible weather, team touchdowns and percentage of plays that end 
# in td/success rate, home or away, player xYAC,
