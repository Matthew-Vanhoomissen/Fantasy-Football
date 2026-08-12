import pandas as pd

from scripts.input_collection.collection_methods import create_csvs_offense
from .player_stats_data import calculate_fantasy_points, extract_player_stats_for_plays


def get_offensive_week_data(
    team_name: str,
    team_data: pd.DataFrame,
    week_input: int
) -> pd.DataFrame | None: 
    """
    Builds a single row of model features for an offesnive in a given week.
    All features use strictly prior week data to prevent leakage.
    Returns None if the team has fewer than 3 games played.

    Args:
            team_name   : NFL team abbreviation (e.g. 'MIA')
            team_data : Play-by-play data for the team
            week_input  : Current week being predicted
    """
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

    return pd.DataFrame({
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
    })


def get_player_position_rank(
    team_name: str,
    player_name: str,
    position: int,
    all_data: pd.DataFrame,
    week_input: int
) -> int | None:
    """
    Calculates the positional ranking of a player on a specific team to resolve
    team importance.
    """

    # === Prior weeks only — no leakage ===
    prior_plays = all_data[
        ((all_data['home_team'] == team_name) | (all_data['away_team'] == team_name)) &
        (all_data['week'] < week_input) & 
        (all_data['posteam'] == team_name)
    ]

    # === Edge case lack of data ===
    if prior_plays.empty:
        return None

    games_played_overall = prior_plays['week'].nunique()

    if games_played_overall < 1:
        return None

    # === Obtain player list for player's team ===
    all_players = pd.concat([
        prior_plays['passer_player_name'],
        prior_plays['rusher_player_name'],
        prior_plays['receiver_player_name']
    ]).dropna().unique()

    # === Iterate through player list ===
    player_averages = []
    for player in all_players:
        p_plays = prior_plays

        p_passing_yards = p_plays[p_plays['passer_player_name'] == player]['passing_yards'].sum()
        p_rushing_yards = p_plays[p_plays['rusher_player_name'] == player]['rushing_yards'].sum()
        p_receiving_yards = p_plays[p_plays['receiver_player_name'] == player]['receiving_yards'].sum()

        p_games = prior_plays[
            (prior_plays['passer_player_name'] == player) |
            (prior_plays['rusher_player_name'] == player) |
            (prior_plays['receiver_player_name'] == player)
        ]['week'].nunique()

        if p_games == 0:
            continue

        total_fp = calculate_fantasy_points(extract_player_stats_for_plays(prior_plays, player))

        avg_fp = total_fp / p_games

        # === Percentage of yards in position ===
        total_yards = p_passing_yards + p_rushing_yards + p_receiving_yards
        if total_yards == 0:
            p_position = -1
        else:
            pass_ratio = p_passing_yards / total_yards
            rush_ratio = p_rushing_yards / total_yards
            rec_ratio = p_receiving_yards / total_yards
            dominance_threshold = 0.45

            if pass_ratio >= dominance_threshold:
                p_position = 0
            elif rush_ratio >= dominance_threshold:
                p_position = 1
            elif rec_ratio >= dominance_threshold:
                p_position = 2
            else:
                p_position = -1

        # === Position filtering ===
        if p_position == position:
            player_averages.append({
                'player_name': player,
                'avg_fantasy_points': avg_fp
            })

    if not player_averages:
        return None

    # === Filter for input player ===
    rankings_df = pd.DataFrame(player_averages)
    rankings_df['rank'] = rankings_df['avg_fantasy_points'].rank(
        ascending=False, method='min'
    ).astype(int)

    player_row = rankings_df[rankings_df['player_name'] == player_name]

    if player_row.empty:
        return None

    return player_row['rank'].values[0]

