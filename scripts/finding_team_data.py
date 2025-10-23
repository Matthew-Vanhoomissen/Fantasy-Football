import pandas as pd 


def get_offensive_data(team_name, team_data): 
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
        (team_data['two_point_attempt'] == 0)
    ]

    # average, total, rush, and passing epa

    total_epa = offensive_plays['epa'].sum()
    total_plays = len(offensive_plays)
    epa_per_play = total_epa / total_plays

    print(f"Total offensive EPA: {total_epa}")
    print(f"Total plays: {total_plays}")
    print(f"EPA per play: {epa_per_play}")

    pass_plays = offensive_plays[
        (offensive_plays['play_type'] == 'pass')
    ]

    total_pass_epa = pass_plays['epa'].sum()
    total_pass_plays = len(pass_plays)
    epa_per_pass = total_pass_epa / total_pass_plays

    print(f"Total pass epa: {total_pass_epa}")
    print(f"EPA per pass: {epa_per_pass}")

    run_plays = offensive_plays[
        (offensive_plays['play_type'] == 'run')
    ]

    total_rush_epa = run_plays['epa'].sum()
    total_rush_plays = len(run_plays)
    epa_per_rush = total_rush_epa / total_rush_plays

    print(f"Total rush epa: {total_rush_epa}")
    print(f"Epa per rush: {epa_per_rush}")

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

    print(f"Total offensive plays: {all_num_plays}")
    print(f"Pass plays: {all_pass_plays} ({pass_percent:.1f}%)")
    print(f"Run plays: {all_rush_plays} ({rush_percent:.1f}%)")

    offensive_stats.append({
        'team_name': team_name,
        'epa_per_play': epa_per_play,
        'epa_per_rush': epa_per_rush,
        'epa_per_pass': epa_per_pass,
        'pass_percent': pass_percent,
        'rush_percent': rush_percent
        
    })

    # Return array
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

    # average, total, rush, and passing epa

    total_epa = offensive_plays['epa'].sum()
    total_plays = len(offensive_plays)
    epa_per_play = total_epa / total_plays

    print(f"Total offensive EPA: {total_epa}")
    print(f"Total plays: {total_plays}")
    print(f"EPA per play: {epa_per_play}")

    pass_plays = offensive_plays[
        (offensive_plays['play_type'] == 'pass')
    ]

    total_pass_epa = pass_plays['epa'].sum()
    total_pass_plays = len(pass_plays)
    epa_per_pass = total_pass_epa / total_pass_plays

    print(f"Total pass epa: {total_pass_epa}")
    print(f"EPA per pass: {epa_per_pass}")

    run_plays = offensive_plays[
        (offensive_plays['play_type'] == 'run')
    ]

    total_rush_epa = run_plays['epa'].sum()
    total_rush_plays = len(run_plays)
    epa_per_rush = total_rush_epa / total_rush_plays

    print(f"Total rush epa: {total_rush_epa}")
    print(f"Epa per rush: {epa_per_rush}")

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

    print(f"Total offensive plays: {all_num_plays}")
    print(f"Pass plays: {all_pass_plays} ({pass_percent:.1f}%)")
    print(f"Run plays: {all_rush_plays} ({rush_percent:.1f}%)")

    offensive_stats.append({
        'week': week,
        'team_name': team_name,
        'epa_per_play': epa_per_play,
        'epa_per_rush': epa_per_rush,
        'epa_per_pass': epa_per_pass,
        'pass_percent': pass_percent,
        'rush_percent': rush_percent
        
    })

    # Return array
    return pd.DataFrame(offensive_stats)