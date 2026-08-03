import pandas as pd
import numpy as np
import pickle

from .defensive_team_data import get_defensive_week_data
from .finding_team_data import get_offensive_week_data
from .player_stats_data import get_player_week_data
from .collection_methods import create_csvs_defense, create_csvs_offense


def get_player_input(player_name, offensive_team_name, defensive_team_name, all_data, week):
   
    defensive_team_data = create_csvs_defense(all_data, defensive_team_name)
    offensive_team_data, player_data = create_csvs_offense(all_data, player_name, offensive_team_name)

    defensive_stats, def_result = get_defensive_week_data(defensive_team_name, defensive_team_data, week)
    offensive_stats = get_offensive_week_data(offensive_team_name, offensive_team_data, week)
    player_stats = get_player_week_data(player_name, offensive_team_name, player_data, all_data, week)

    # TODO This will return null during biweek because it can't find opponent. Make another method
    #      that can be used by the frontend
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


def get_prediction(player1_name, player2_name, week, name_file, all_data_current, all_data_past):
    if convert(player1_name, name_file) is None or convert(player2_name, name_file) is None:
        return None, None, None, "NPF"

    p1, p1_t, pos1 = convert(player1_name, name_file)
    print(p1_t)
    print(p1)
    p1_d = return_opponent(p1_t, week, 2025)

    p2, p2_t, pos2 = convert(player2_name, name_file)
    print(p2_t)
    print(p2)
    p2_d = return_opponent(p2_t, week, 2025)

    r1, display1, result1 = get_player_input(p1, p1_t, p1_d, all_data_current, week)
    r2, display2, result2 = get_player_input(p2, p2_t, p2_d, all_data_current, week)

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


def convert(name, file):
    SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
    override = pd.read_csv("data/override.csv", low_memory=False)

    full_name = name.split(" ", 1)
    if len(full_name) != 2:
        return None
    
    last_name = full_name[1]
    first_name = full_name[0]
    first_initial = first_name[0]

    last_parts_raw = last_name.replace(".", " ").split()
    last_parts = []
    for part in last_parts_raw:
        if part.lower() not in SUFFIXES:
            if part == "St ":
                last_parts.append(part + ".")
            else:
                last_parts.append(part)
    
    cleaned_last = ""
    for part in last_parts:
        cleaned_last = cleaned_last + part
    
    player = file[(file['first_name'] == first_name) & (file['last_name'] == last_name)]

    match = override[override['player_name'] == name]
    if not match.empty:
        abbr = match.iloc[0]['abbreviation']
        player = player.iloc[0]
        team = player['team']
        if team == "LAR":
            team = "LA"
        elif team == "WSH":
            team = "WAS"
        return abbr, team, player['position']

    if player.empty:
        return None
    else:
        player = player.iloc[0]
        
        # Find all players with the same last name AND same first initial
        same_last_and_initial = file[
            (file['last_name'] == last_name) & 
            (file['first_name'].str[0] == first_initial)
        ].sort_values('first_name')
        
        if len(same_last_and_initial) == 1:
            # Only one player with this last name and first initial
            abbr = first_name[0] + "." + cleaned_last
        else:
            # Multiple players with same initial
            all_first_names = same_last_and_initial['first_name'].tolist()
            
            # Find this player's position in alphabetical order
            player_index = all_first_names.index(first_name)
            
            # Check only players that come BEFORE this one alphabetically
            chars_needed = 1
            for i in range(player_index):
                other_first = all_first_names[i]
                # Find how many chars needed to differentiate from this earlier player
                temp_chars = 1
                while temp_chars <= min(len(first_name), len(other_first)):
                    if first_name[:temp_chars] != other_first[:temp_chars]:
                        break
                    temp_chars += 1
                chars_needed = max(chars_needed, temp_chars)
            
            abbr = first_name[:chars_needed] + "." + cleaned_last
        team = player['team']
        if team == "LAR":
            team = "LA"
        elif team == "WSH":
            team = "WAS"
        return abbr, team, player['position']


def return_opponent(team, week, season):
    schedule = pd.read_csv(f"data/schedule_{season}.csv")

    schedule = schedule[schedule["week"] == week]

    away = schedule[schedule['away_team'] == team]
    if not away.empty:
        return (away.iloc[0])['home_team']
    home = schedule[schedule['home_team'] == team]
    if not home.empty:
        return (home.iloc[0])['away_team']

    return None
