import pandas as pd
from .target_percentage import get_week_percentage
from .finding_team_data import get_player_position_rank


# ============================================================
# FANTASY POINTS CALCULATION
# ============================================================

def calculate_fantasy_points(
    passing_yards: float,
    rushing_yards: float,
    receiving_yards: float,
    receptions: int,
    interceptions: int,
    fumbles_lost: int,
    pass_td: int,
    rush_td: int,
    rec_td: int,
    two_pt_pass: int,
    two_pt_rush: int,
    two_pt_rec: int
) -> float:
    """
    Calculates PPR fantasy points from raw stat inputs.
    Scoring: 0.04/passing yard, 0.1/rushing yard, 0.1/receiving yard,
             1/reception, 4/pass TD, 6/rush TD, 6/rec TD,
             -2/interception, -2/fumble lost, 2/two-point conversion
    """
    return (
        (passing_yards   * 0.04) +
        (rushing_yards   * 0.10) +
        (receiving_yards * 0.10) +
        (receptions            ) -
        (interceptions   * 2   ) +
        (pass_td         * 4   ) +
        (rush_td         * 6   ) +
        (rec_td          * 6   ) -
        (fumbles_lost    * 2   ) +
        (two_pt_pass     * 2   ) +
        (two_pt_rush     * 2   ) +
        (two_pt_rec      * 2   )
    )


def extract_player_stats_for_plays(plays: pd.DataFrame, player_name: str) -> dict:
    """
    Extracts all raw counting stats for a player from a set of plays.
    Returns a dict of raw totals ready for fantasy point calculation.
    """
    passing_plays   = plays[plays['passer_player_name']   == player_name]
    rushing_plays   = plays[plays['rusher_player_name']   == player_name]
    receiving_plays = plays[plays['receiver_player_name'] == player_name]

    return {
        'passing_yards'   : passing_plays['passing_yards'].sum(),
        'rushing_yards'   : rushing_plays['rushing_yards'].sum(),
        'receiving_yards' : receiving_plays['receiving_yards'].sum(),
        'receptions'      : len(receiving_plays[receiving_plays['complete_pass'] == 1]),
        'interceptions'   : passing_plays['interception'].sum(),
        'fumbles_lost'    : plays[plays['fumbled_1_player_name'] == player_name]['fumble_lost'].sum(),
        'pass_td'         : passing_plays['pass_touchdown'].sum(),
        'rush_td'         : rushing_plays['rush_touchdown'].sum(),
        'rec_td'          : receiving_plays['pass_touchdown'].sum(),
        'two_pt_pass'     : (passing_plays['two_point_conv_result']   == 'success').sum(),
        'two_pt_rush'     : (rushing_plays['two_point_conv_result']   == 'success').sum(),
        'two_pt_rec'      : (receiving_plays['two_point_conv_result'] == 'success').sum(),
    }


def _calculate_boom_bust_metrics(
    prior_plays: pd.DataFrame,
    player_name: str,
    average_fp: float,
    weeks: list,
    threshold: float = 6.0
) -> dict:
    """
    Calculates boom/bust game counts and average point differentials.
    A boom game exceeds the player average by threshold points.
    A bust game falls below the player average by threshold points.
    """
    positive_diffs = []
    negative_diffs = []

    for week_num in weeks:
        week_plays = prior_plays[prior_plays['week'] == week_num]
        raw        = extract_player_stats_for_plays(week_plays, player_name)
        week_fp    = calculate_fantasy_points(**raw)
        diff       = week_fp - average_fp

        if diff > threshold:
            positive_diffs.append(diff)
        elif diff < -threshold:
            negative_diffs.append(diff)

    boom_games = len(positive_diffs)
    bust_games = len(negative_diffs)

    return {
        'boom_games'  : boom_games,
        'bust_games'  : bust_games,
        'boom_points' : sum(positive_diffs) / boom_games if boom_games > 0 else 0,
        'bust_points' : sum(negative_diffs) / bust_games if bust_games > 0 else 0,
    }


def _calculate_recent_average(
    prior_plays: pd.DataFrame,
    player_name: str,
    weeks: list,
    n_weeks: int = 3
) -> float:
    """
    Calculates the average fantasy points over the last n_weeks games.
    """
    recent_total  = 0.0
    weeks_counted = 0

    for week in weeks[-n_weeks:]:
        week_plays = prior_plays[prior_plays['week'] == week]
        raw        = extract_player_stats_for_plays(week_plays, player_name)
        recent_total  += calculate_fantasy_points(**raw)
        weeks_counted += 1

    return recent_total / weeks_counted if weeks_counted > 0 else 0.0


# ============================================================
# PLAYER DATA POINTS BUILDER
# ============================================================

def get_player_week_data(
    player_name: str,
    team_name: str,
    player_data: pd.DataFrame,
    all_stats: pd.DataFrame,
    week_input: int,
    position: int
) -> pd.DataFrame | None:
    """
    Builds a single row of model features for a player in a given week.
    All features use strictly prior week data to prevent leakage.
    Returns None if the player has fewer than 3 games played.

    Args:
        player_name : Abbreviated player name (e.g. 'T.Hill')
        team_name   : NFL team abbreviation (e.g. 'MIA')
        player_data : Play-by-play data for the player's team
        all_stats   : Full play-by-play data across all teams
        week_input  : Current week being predicted
        position    : Encoded position (0=QB, 1=RB, 2=WR/TE, 3=FLEX, -1=Unknown)
    """

    # === Prior weeks only — no leakage ===
    prior_plays  = player_data[player_data['week'] < week_input]
    games_played = prior_plays['week'].nunique()

    if games_played < 3:
        return None

    # === Current week target variable ===
    current_week_plays = player_data[player_data['week'] == week_input]
    cw_raw             = extract_player_stats_for_plays(current_week_plays, player_name)
    week_fantasy_points = calculate_fantasy_points(**cw_raw)

    # === Season averages (prior weeks) ===
    season_raw      = extract_player_stats_for_plays(prior_plays, player_name)
    total_fp        = calculate_fantasy_points(**season_raw)
    average_fp      = total_fp / games_played

    average_p_yards   = season_raw['passing_yards']   / games_played
    average_r_yards   = season_raw['rushing_yards']   / games_played
    average_rec_yards = season_raw['receiving_yards'] / games_played

    # === Boom / bust metrics ===
    weeks        = sorted(prior_plays['week'].unique())
    boom_bust    = _calculate_boom_bust_metrics(prior_plays, player_name, average_fp, weeks)

    # === Recent form ===
    three_week_avg      = _calculate_recent_average(prior_plays, player_name, weeks)
    last_three_weeks_diff = three_week_avg - average_fp

    # === Red zone usage ===
    red_zone_plays   = prior_plays[prior_plays['yardline_100'] <= 20]
    red_zone_targets = red_zone_plays[red_zone_plays['receiver_player_name'] == player_name].shape[0]
    red_zone_carries = red_zone_plays[red_zone_plays['rusher_player_name']   == player_name].shape[0]

    # === Completion percentage ===
    pass_attempts      = prior_plays[
        (prior_plays['passer_player_name'] == player_name) &
        (prior_plays['play_type']          == 'pass')
    ]
    completions        = pass_attempts[pass_attempts['complete_pass'] == 1].shape[0]
    completion_pct     = completions / pass_attempts.shape[0] if pass_attempts.shape[0] > 0 else 0.0

    # === Positional ranking within team ===
    position_ranking = get_player_position_rank(
        team_name, player_name, position, all_stats, week_input
    )
    
    # === External percentage features ===
    percentages = get_week_percentage(team_name, player_name, all_stats, week_input)

    # === Assemble feature row ===
    player_stats = [{
        'week'                 : week_input,
        'team_name'            : team_name,
        'player_name'          : player_name,
        'position'             : position,
        'position_ranking'     : position_ranking,
        'average_passing_yards': average_p_yards,
        'average_rushing_yards': average_r_yards,
        'average_recieving_yards': average_rec_yards,
        'receptions_avg'       : season_raw['receptions']    / games_played,
        'passing_tds_avg'      : season_raw['pass_td']       / games_played,
        'rushing_tds_avg'      : season_raw['rush_td']       / games_played,
        'recieving_tds_avg'    : season_raw['rec_td']        / games_played,
        'average_fantasy_points': average_fp,
        'week_fantasy_points'  : week_fantasy_points,
        'bust_percent'         : boom_bust['bust_games']  / games_played,
        'bust_points_average'  : boom_bust['bust_points'],
        'boom_percent'         : boom_bust['boom_games']  / games_played,
        'boom_points_average'  : boom_bust['boom_points'],
        'last_three_weeks_diff': last_three_weeks_diff,
        'redzone_carries'      : red_zone_carries,
        'redzone_targets'      : red_zone_targets,
        'completion_percentage': completion_pct,
    }]

    return pd.merge(pd.DataFrame(player_stats), percentages, how='left')


# ============================================================
# PLAYER / TEAM LOOKUP UTILITIES
# ============================================================

def get_player_team(all_data: pd.DataFrame, player_name: str) -> str | None:
    """
    Returns the offensive team abbreviation a player most frequently
    appeared for across all available play-by-play data.
    """
    player_plays = all_data[
        (all_data['passer_player_name']   == player_name) |
        (all_data['rusher_player_name']   == player_name) |
        (all_data['receiver_player_name'] == player_name)
    ]

    if player_plays.empty:
        return None

    return player_plays['posteam'].mode()[0]


def get_opponent_team(
    all_data: pd.DataFrame,
    offensive_team_name: str,
    week: int
) -> str | None:
    """
    Returns the defensive team abbreviation that faced the given
    offensive team in the specified week.
    """
    week_data = all_data[
        (all_data['week']    == week) &
        (all_data['posteam'] == offensive_team_name)
    ]

    if week_data.empty:
        return None

    return week_data['defteam'].mode()[0]


def did_player_play_this_week(
    player_data: pd.DataFrame,
    player_name: str,
    week: int
) -> bool:
    """
    Returns True if the player recorded any statistical activity
    in the given week. Used to filter out bye weeks and inactive
    players from the training dataset.
    """
    week_plays = player_data[player_data['week'] == week]

    return (
        week_plays[week_plays['passer_player_name']   == player_name]['passing_yards'].sum()  > 0 or
        week_plays[week_plays['rusher_player_name']   == player_name]['rushing_yards'].sum()  > 0 or
        week_plays[week_plays['receiver_player_name'] == player_name]['receiving_yards'].sum() > 0 or
        not week_plays[week_plays['receiver_player_name'] == player_name].empty
    )