import pandas as pd


def get_defensive_week_data(
    team_name: str,
    team_data: pd.DataFrame,
    week: int
) -> tuple[pd.DataFrame, str] | tuple[None, str]:
    """
    Builds a single row of model features for a defense in a given week.
    All features use strictly prior week data to prevent leakage.
    Returns None if the team has fewer than 3 games played.

    Args:
        team_name   : NFL team abbreviation (e.g. 'MIA')
        team_data   : Play-by-play data for the team
        week_input  : Current week being predicted
    """
    # === Defensive plays ===
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
        (team_data['td_team'] != team_name) &
        (team_data['week'] < week)
    ]

    if len(defensive_plays) == 0:
        if week == 1:
            return None, "W1"
        return None, "BW"
    
    games_played = defensive_plays['week'].nunique()

    # === Team yards ===
    passing_yards = defensive_plays[defensive_plays['play_type'] == 'pass']['passing_yards'].sum()

    rushing_yards = defensive_plays[defensive_plays['play_type'] == 'run']['rushing_yards'].sum()

    sack_yards = team_data[
        (team_data['defteam'] == team_name) & 
        (team_data['sack'] == 1) &
        (team_data['week'] < week)
    ]['yards_gained'].sum()

    # === EPA against defense ===
    epa_against = defensive_plays['epa'].sum()
    epa_per_play = epa_against / len(defensive_plays)

    epa_pass_against = defensive_plays[defensive_plays['play_type'] == 'pass']['epa'].sum()
    pass_epa_play = epa_pass_against / len(defensive_plays[defensive_plays['play_type'] == 'pass'])

    epa_rush_against = defensive_plays[defensive_plays['play_type'] == 'run']['epa'].sum()
    rush_epa_play = epa_rush_against / len(defensive_plays[defensive_plays['play_type'] == 'run'])

    # === Allowed scores ===
    touchdowns_allowed = defensive_plays['touchdown'].sum()
    field_goals_allowed = defensive_plays['field_goal_result'].apply(lambda x: 1 if x == 'made' else 0).sum()
    extra_points_allowed = defensive_plays['extra_point_result'].apply(lambda x: 1 if x == 'good' else 0).sum()
    two_point_conversions = defensive_plays['two_point_conv_result'].apply(lambda x: 1 if x == 'success' else 0).sum()

    points_allowed = ((touchdowns_allowed * 6) + (field_goals_allowed * 3) + extra_points_allowed + (two_point_conversions * 2)) / games_played

    # === Allowed third and fourth down conversion rate ===
    all_third_downs = len(team_data[team_data['down'] == 3.0])
    all_fourth_downs = len(team_data[team_data['down'] == 4.0])

    converted_third_downs = len(team_data[team_data['third_down_converted'] == 1.0])
    converted_fourth_downs = len(team_data[team_data['fourth_down_converted'] == 1.0])

    third_down_completion = converted_third_downs / all_third_downs if all_third_downs > 0 else 0
    fourth_down_completion = converted_fourth_downs / all_fourth_downs if all_fourth_downs > 0 else 0

    return pd.DataFrame({
        'week': week,
        'team_name': team_name,
        'allowed_passing_yards': passing_yards / games_played,
        'allowed_rushing_yards': rushing_yards / games_played,
        'sack_yards': sack_yards / games_played,
        'avg_epa_against': epa_per_play,
        'pass_epa_against': pass_epa_play,
        'rush_epa_against': rush_epa_play,
        'points_against': points_allowed,
        'third_down_allowed': third_down_completion,
        'fourth_down_allowed': fourth_down_completion
        
    }), "success"
