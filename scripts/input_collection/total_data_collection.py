import pandas as pd
import numpy as np
import pickle

from .defensive_team_data import get_defensive_week_data
from .finding_team_data import get_offensive_week_data
from .player_stats_data import get_player_week_data
from .collection_methods import create_csvs_defense, create_csvs_offense, convert, return_opponent

# For weekly data collection
from scripts.data_collection.fetch_raw_data import get_season_data
from scripts.data_collection.get_player_names import get_names
from scripts.csv_manipulation.edit_names import edit_player_names
from scripts.csv_manipulation.shrink_csv import edit_data

# ============================================================
# MODEL INPUT REQUEST COLLECTION
# ============================================================

CURRENT_SEASON = 2026

def get_player_input(
    player_name: str,
    offensive_team_name: str,
    defensive_team_name: str,
    all_data: pd.DataFrame,
    week: int,
    position: int
) -> tuple[None, None, str] | tuple[float, dict, str]:
    """
    Collects player, offensive and defensive team data based on requested players and
    input week through historic play-by-play data. Data is input into XGBoost model to
    retrieve predicted deviation from average to return predicted points.

    Args:
        player_name           : Abbreviated player name (e.g. 'T.Hill')
        offensive_team_name   : NFL team abbreviation (e.g. 'MIA')
        defensive_team_name   : NFL team abbreviation (e.g. 'BAL')
        all_data              : Fully loaded play-by-play data for current season
        week                  : Current week being predicted
        position              : Encoded position (0=QB, 1=RB, 2=WR/TE, 3=FLEX, -1=Unknown)
    """
   
    defensive_team_data = create_csvs_defense(all_data, defensive_team_name)
    offensive_team_data, player_data = create_csvs_offense(all_data, player_name, offensive_team_name)

    defensive_stats, def_result = get_defensive_week_data(defensive_team_name, defensive_team_data, week)
    offensive_stats = get_offensive_week_data(offensive_team_name, offensive_team_data, week)
    player_stats = get_player_week_data(player_name, offensive_team_name, player_data, all_data, week, position)

    if defensive_stats is None:
        return None, None, def_result

    if offensive_stats is None or player_stats is None:
        return None, None, "NDF"

    offensive_stats = offensive_stats.rename(columns={"team_name": "off_team_name"})
    defensive_stats = defensive_stats.rename(columns={"team_name": "def_team_name"})
    player_stats = player_stats.rename(columns={"team_name": "off_team_name"})

    player_stats["def_team_name"] = defensive_team_name

    data = (
        player_stats
        .merge(offensive_stats, on="off_team_name", how="left")
        .merge(defensive_stats, how="left", left_on="def_team_name", right_on="def_team_name")
    )

    data['recent_momentum'] = data['last_three_weeks_diff'] + data['average_fantasy_points']

    feature_cols = [
        "receptions_avg", "average_passing_yards", "average_rushing_yards",
        "average_recieving_yards", "passing_tds_avg", "rushing_tds_avg",
        "recieving_tds_avg", "bust_points_average",
        "bust_percent", "boom_points_average", "boom_percent",
        "passing_target_percentage", "rushing_percentage",
        "epa_per_rush", "epa_per_pass", "pass_percent", "rush_percent",
        "allowed_passing_yards", "allowed_rushing_yards", "sack_yards",
        "pass_epa_against", "rush_epa_against", "points_against",
        "position", "redzone_carries", "redzone_targets", "completion_percentage",
        "fourth_down_allowed", "third_down_allowed", "fourth_down_completion",
        "third_down_completion", "success_rate", "home_team", "position_ranking",
        "win_percentage", "recent_momentum"
    ]

    with open('models/fantasy_model_final.pkl', 'rb') as f:
        model_data = pickle.load(f)
        xgb_model = model_data['model']

    x = data[feature_cols]
    x = x.replace([np.inf, -np.inf], np.nan).fillna(0)

    projection = xgb_model.predict(x)
    
    result = projection + player_stats.get('average_fantasy_points')

    display_cols = [
        "last_three_weeks_diff", "average_fantasy_points", "average_passing_yards", "bust_percent", 
        "success_rate", "average_recieving_yards", "average_rushing_yards", "boom_percent", 
        "boom_points_average", "bust_points_average", "epa_per_pass", "epa_per_rush", "recent_momentum"
    ]
    display_data = data[display_cols]

    return result.iloc[0], display_data.iloc[0].to_dict(), "success"


def get_prediction(player1_name, player2_name, week, name_file, all_data_current, all_data_past, override_name_file):
    p1, p1_t, pos1 = convert(player1_name, name_file, override_name_file)
    p2, p2_t, pos2 = convert(player2_name, name_file, override_name_file)
    if p1 is None or p2 is None:
        return None, None, None, "NPF"

    # Assign position as number
    pos1 = position_converter(pos1)
    pos2 = position_converter(pos2)

    print(p1_t)
    print(p1)
    p1_d = return_opponent(p1_t, week, 2025)
    
    print(p2_t)
    print(p2)
    p2_d = return_opponent(p2_t, week, 2025)

    r1, display1, result1 = get_player_input(p1, p1_t, p1_d, all_data_current, week, pos1)
    r2, display2, result2 = get_player_input(p2, p2_t, p2_d, all_data_current, week, pos2)

    print(r1)
    print(r2)
    result = "success"
    if r1 is None or r2 is None:
        if result1 == "BW" or result2 == "BW":
            print("BW")
            return None, None, None, "BW"
        else:
            result = "NDF"
            if r1 is None:
                r1, display1, result1 = get_player_input(p1, p1_t, p1_d, all_data_past, 19)
            if r2 is None:
                r2, display2, result2 = get_player_input(p2, p2_t, p2_d, all_data_past, 19)
            if r1 is None or r2 is None:
                return None, None, None, result
            result = "ODF"  # Old data found

    if r1 > r2:
        winner = 1
    else:
        winner = 2
    
    display1['position'] = pos1
    display1['team'] = p1_t

    display2['position'] = pos2
    display2['team'] = p2_t

    print(winner)
    return {"winner": winner}, display1, display2, result


def position_converter(position):
    if position == "QB":
        return 0
    elif position == "RB" or position == "FB":
        return 1
    elif position == "WR" or position == "TE":
        return 2
    else:
        return -1


def weekly_data_collection():
    get_season_data(CURRENT_SEASON)
    edit_data(CURRENT_SEASON)

    get_season_data(CURRENT_SEASON - 1)
    edit_data(CURRENT_SEASON)

    get_names()
    edit_player_names()


if __name__ == "__main__":
    weekly_data_collection()
