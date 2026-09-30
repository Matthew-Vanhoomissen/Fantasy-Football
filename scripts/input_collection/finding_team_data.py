import pandas as pd


def get_offensive_week_data(
    team_name: str,
    team_data: pd.DataFrame,
    week_input: int
) -> pd.DataFrame | None:
    """
    Builds a single row of model features for an offense in a given week.
    All features use strictly prior week data to prevent leakage.
    Returns None if the team has fewer than 3 games played.

    Args:
        team_name   : NFL team abbreviation (e.g. 'MIA')
        team_data   : Play-by-play data for the team
        week_input  : Current week being predicted
    """
    # === Offensive plays ===
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
        (team_data['week'] < week_input)
    ]
    games_played = offensive_plays['week'].nunique()
    if games_played < 3:
        return None

    # === EPA Calculation ===
    total_epa = offensive_plays['epa'].sum()
    total_plays = games_played
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

    # === Play selection percentage ===
    all_num_plays = len(offensive_plays)
    all_pass_plays = len(offensive_plays[offensive_plays['play_type'] == 'pass'])
    all_rush_plays = len(offensive_plays[offensive_plays['play_type'] == 'run'])

    pass_percent = (all_pass_plays / all_num_plays) * 100
    rush_percent = (all_rush_plays / all_num_plays) * 100

    # === Third and fourth down conversion ===
    all_third_downs = len(offensive_plays[offensive_plays['down'] == 3.0])
    all_fourth_downs = len(offensive_plays[offensive_plays['down'] == 4.0])

    converted_third_downs = len(offensive_plays[offensive_plays['third_down_converted'] == 1.0])
    converted_fourth_downs = len(offensive_plays[offensive_plays['fourth_down_converted'] == 1.0])

    third_down_completion = converted_third_downs / all_third_downs if all_third_downs > 0 else 0
    fourth_down_completion = converted_fourth_downs / all_fourth_downs if all_fourth_downs > 0 else 0

    # === Success rate/Scoring percentage ===
    total_drives = offensive_plays.groupby('week')['down'].nunique().sum()

    successful_drives_df = offensive_plays[(offensive_plays['touchdown'] == 1) | (offensive_plays['field_goal_result'] == "made")]
    successful_drives = successful_drives_df.groupby('week')['down'].nunique().sum()

    success_rate = successful_drives / total_drives if total_drives > 0 else 0

    # === Team and game result ===
    home_team = 1 if offensive_plays.iloc[0]['home_team'] == team_name else 0

    total_games = len(offensive_plays['week'].unique())

    won_games = len(offensive_plays[
        ((offensive_plays['home_team'] == team_name) & (offensive_plays['result'] > 0)) | 
        ((offensive_plays['away_team'] == team_name) & (offensive_plays['result'] < 0))
    ]['week'].unique())

    tied_games = len(offensive_plays[offensive_plays['result'] == 0]['week'].unique())

    return pd.DataFrame([{
        'week'                  : week_input,
        'team_name'             : team_name,
        'epa_per_play'          : epa_per_play,
        'epa_per_rush'          : epa_per_rush,
        'epa_per_pass'          : epa_per_pass,
        'pass_percent'          : pass_percent,
        'rush_percent'          : rush_percent,
        'third_down_completion' : third_down_completion,
        'fourth_down_completion': fourth_down_completion,
        'success_rate'          : success_rate,
        'home_team'             : home_team,
        'win_percentage'        : (won_games + (tied_games / 2)) / total_games
    }])

