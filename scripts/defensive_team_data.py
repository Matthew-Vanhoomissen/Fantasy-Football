import pandas as pd


def get_defensive_data(team_nameI, team_data): 
    # Make empty array
    defensive_stats = []

    team_name = team_nameI

    # all defensive plays
    defensive_plays = team_data[
        (team_data['defteam'] == team_name) & 
        (team_data['play_type'].isin(['pass', 'run'])) &
        (team_data['kickoff_attempt'] == 0) &
        (team_data['extra_point_attempt'] == 0) &
        (team_data['epa'].notna()) &
        (team_data['qb_kneel'] == 0) &
        (team_data['qb_spike'] == 0) &
        (team_data['penalty'] == 0) & 
        (team_data['two_point_attempt'] == 0)
    ]

    # allowed passing yards
    passing_yards = defensive_plays[defensive_plays['play_type'] == 'pass']['passing_yards'].sum()
    print(f"Allowed {passing_yards} passing yards")

    # allowed rushing yards
    rushing_yards = defensive_plays[defensive_plays['play_type'] == 'run']['rushing_yards'].sum()
    print(f"Allowed {rushing_yards} rushing yards")

    # Penalty yards against defense (positive for offense)
    penalty_yards = team_data[
        (team_data['defteam'] == team_name) & 
        (team_data['penalty_team'] == team_name)
    ]['penalty_yards'].sum()
    print(f"Penalty yards {penalty_yards}")

    # Sack yards (negative)
    sack_yards = team_data[
        (team_data['defteam'] == team_name) & 
        (team_data['sack'] == 1)
    ]['yards_gained'].sum()
    print(f"Sack yards {sack_yards}")
    print(penalty_yards + sack_yards + passing_yards)

    # total epa against
    epa_against = defensive_plays['epa'].sum()
    epa_per_play = epa_against / len(defensive_plays)
    print(f"Total epa against the defense: {epa_against}")
    print(f"General epa per play {epa_per_play}")

    # pass epa against
    epa_pass_against = defensive_plays[defensive_plays['play_type'] == 'pass']['epa'].sum()
    pass_epa_play = epa_pass_against / len(defensive_plays[defensive_plays['play_type'] == 'pass'])
    print(f"average pass epa against: {pass_epa_play}")

    # rush epa against
    epa_rush_against = defensive_plays[defensive_plays['play_type'] == 'run']['epa'].sum()
    rush_epa_play = epa_rush_against / len(defensive_plays[defensive_plays['play_type'] == 'run'])
    print(f"average rush epa against: {rush_epa_play}")

    # points allowed

    teamDef_data = team_data[(team_data['defteam'] == team_name) &
                             (team_data['td_team'] != team_name)]

    touchdowns_allowed = teamDef_data['touchdown'].sum()
    field_goals_allowed = teamDef_data['field_goal_result'].apply(lambda x: 1 if x == 'made' else 0).sum()
    extra_points_allowed = teamDef_data['extra_point_result'].apply(lambda x: 1 if x == 'good' else 0).sum()
    two_point_conversions = teamDef_data['two_point_conv_result'].apply(lambda x: 1 if x == 'success' else 0).sum()

    points_allowed = (touchdowns_allowed * 6) + (field_goals_allowed * 3) + extra_points_allowed + (two_point_conversions * 2)

    print(f"Total points allowed by {team_name} defense: {points_allowed}")

    defensive_stats.append({
        'team_name': team_name,
        'allowed_passing_yards': passing_yards,
        'allowed_rushing_yards': rushing_yards,
        'sack_yards': sack_yards,
        'total_epa_against': epa_against,
        'pass_epa_against': pass_epa_play,
        'rush_epa_against': rush_epa_play,
        'points_against': points_allowed
        
    })

    return pd.DataFrame(defensive_stats)


def get_defensive_week_data(team_nameI, team_data, week): 
    # Make empty array
    defensive_stats = []

    team_name = team_nameI

    # all defensive plays
    defensive_plays = team_data[
        (team_data['defteam'] == team_name) & 
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

    if len(defensive_plays) == 0:
        return None
    
    games_played = defensive_plays['week'].nunique()

    # allowed passing yards
    passing_yards = defensive_plays[defensive_plays['play_type'] == 'pass']['passing_yards'].sum()

    # allowed rushing yards
    rushing_yards = defensive_plays[defensive_plays['play_type'] == 'run']['rushing_yards'].sum()

    # Penalty yards against defense (positive for offense)
    penalty_yards = team_data[
        (team_data['defteam'] == team_name) & 
        (team_data['penalty_team'] == team_name)
    ]['penalty_yards'].sum()

    # Sack yards (negative)
    sack_yards = team_data[
        (team_data['defteam'] == team_name) & 
        (team_data['sack'] == 1) &
        (team_data['week'] < week)
    ]['yards_gained'].sum()

    # total epa against
    epa_against = defensive_plays['epa'].sum()
    epa_per_play = epa_against / len(defensive_plays)

    # pass epa against
    epa_pass_against = defensive_plays[defensive_plays['play_type'] == 'pass']['epa'].sum()
    pass_epa_play = epa_pass_against / len(defensive_plays[defensive_plays['play_type'] == 'pass'])

    # rush epa against
    epa_rush_against = defensive_plays[defensive_plays['play_type'] == 'run']['epa'].sum()
    rush_epa_play = epa_rush_against / len(defensive_plays[defensive_plays['play_type'] == 'run'])

    # points allowed

    teamDef_data = team_data[(team_data['defteam'] == team_name) &
                             (team_data['td_team'] != team_name) &
                             (team_data['week'] < week)]

    touchdowns_allowed = teamDef_data['touchdown'].sum()
    field_goals_allowed = teamDef_data['field_goal_result'].apply(lambda x: 1 if x == 'made' else 0).sum()
    extra_points_allowed = teamDef_data['extra_point_result'].apply(lambda x: 1 if x == 'good' else 0).sum()
    two_point_conversions = teamDef_data['two_point_conv_result'].apply(lambda x: 1 if x == 'success' else 0).sum()

    points_allowed = ((touchdowns_allowed * 6) + (field_goals_allowed * 3) + extra_points_allowed + (two_point_conversions * 2)) / games_played

    defensive_stats.append({
        'week': week,
        'team_name': team_name,
        'allowed_passing_yards': passing_yards / games_played,
        'allowed_rushing_yards': rushing_yards / games_played,
        'sack_yards': sack_yards / games_played,
        'avg_epa_against': epa_per_play,
        'pass_epa_against': pass_epa_play,
        'rush_epa_against': rush_epa_play,
        'points_against': points_allowed / games_played
        
    })

    return pd.DataFrame(defensive_stats)