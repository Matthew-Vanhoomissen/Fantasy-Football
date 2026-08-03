import pandas as pd

from scripts.input_collection.collection_methods import create_csvs_offense

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

    # Win percentage
    total_games = len(all_plays['week'].unique())

    won_games = len(all_plays[
        ((all_plays['home_team'] == team_name) & (all_plays['result'] > 0)) | 
        ((all_plays['away_team'] == team_name) & (all_plays['result'] < 0))
    ]['week'].unique())

    tied_games = len(all_plays[all_plays['result'] == 0]['week'].unique())

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
        'home_team': home_team,
        'win_percentage': (won_games + (tied_games / 2)) / total_games
    })

    return pd.DataFrame(offensive_stats)


# TODO
# Possible new inputs: vegas odds, offensive team 3rd and 4th down conversions, defensive conversion allow rate,
# completion percentage + advnaced cpoe, possible weather, team touchdowns and percentage of plays that end 
# in td/success rate, home or away, player xYAC,
def get_player_position_rank(team_name, player_name, position, all_data, week_input):

    prior_plays = all_data[
        ((all_data['home_team'] == team_name) | (all_data['away_team'] == team_name)) &
        (all_data['week'] < week_input) & 
        (all_data['posteam'] == team_name)
    ]

    if prior_plays.empty:
        return None

    games_played_overall = prior_plays['week'].nunique()

    if games_played_overall < 1:
        return None

    # Get all players who appear in the prior plays for this team
    # by combining all player name columns
    all_players = pd.concat([
        prior_plays['passer_player_name'],
        prior_plays['rusher_player_name'],
        prior_plays['receiver_player_name']
    ]).dropna().unique()

    player_averages = []

    for p in all_players:
        p_plays = prior_plays

        p_passing_yards = p_plays[p_plays['passer_player_name'] == p]['passing_yards'].sum()
        p_rushing_yards = p_plays[p_plays['rusher_player_name'] == p]['rushing_yards'].sum()
        p_receiving_yards = p_plays[p_plays['receiver_player_name'] == p]['receiving_yards'].sum()
        p_receptions = len(p_plays[(p_plays['receiver_player_name'] == p) & 
                                    (p_plays['complete_pass'] == 1)])
        p_interceptions = p_plays[p_plays['passer_player_name'] == p]['interception'].sum()
        p_fumbles_lost = p_plays[p_plays['fumbled_1_player_name'] == p]['fumble_lost'].sum()
        p_pass_td = p_plays[p_plays['passer_player_name'] == p]['pass_touchdown'].sum()
        p_rush_td = p_plays[p_plays['rusher_player_name'] == p]['rush_touchdown'].sum()
        p_rec_td = p_plays[p_plays['receiver_player_name'] == p]['pass_touchdown'].sum()
        p_two_pt_pass = (p_plays[p_plays['passer_player_name'] == p]['two_point_conv_result'] == 'success').sum()
        p_two_pt_rush = (p_plays[p_plays['rusher_player_name'] == p]['two_point_conv_result'] == 'success').sum()
        p_two_pt_rec = (p_plays[p_plays['receiver_player_name'] == p]['two_point_conv_result'] == 'success').sum()

        p_games = prior_plays[
            (prior_plays['passer_player_name'] == p) |
            (prior_plays['rusher_player_name'] == p) |
            (prior_plays['receiver_player_name'] == p)
        ]['week'].nunique()

        if p_games == 0:
            continue

        total_fp = (
            (p_passing_yards * 0.04) +
            (p_rushing_yards * 0.1) +
            (p_receiving_yards * 0.1) -
            (p_interceptions * 2) +
            (p_pass_td * 4) +
            (p_rush_td * 6) +
            (p_rec_td * 6) -
            (p_fumbles_lost * 2) +
            (p_receptions) +
            (p_two_pt_pass * 2) +
            (p_two_pt_rec * 2) +
            (p_two_pt_rush * 2)
        )

        avg_fp = total_fp / p_games

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

        # Only include players at the same position
        if p_position == position:
            player_averages.append({
                'player_name': p,
                'avg_fantasy_points': avg_fp
            })

    if not player_averages:
        return None

    rankings_df = pd.DataFrame(player_averages)
    rankings_df['rank'] = rankings_df['avg_fantasy_points'].rank(
        ascending=False, method='min'
    ).astype(int)

    player_row = rankings_df[rankings_df['player_name'] == player_name]

    if player_row.empty:
        return None

    return player_row['rank'].values[0]

