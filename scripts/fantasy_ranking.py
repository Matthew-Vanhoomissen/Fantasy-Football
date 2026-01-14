import pandas as pd 
from make_csv import create_csvs_offense
from name_formatter import convert


def get_fantasy_sum(player_name, team, data):
    team_data, player_data = create_csvs_offense(data, player_name, team)

    week_only_data = team_data

    two_pt_pass_WN = (week_only_data[week_only_data['passer_player_name'] == player_name]['two_point_conv_result'] == 'success').sum()
    two_pt_rush_WN = (week_only_data[week_only_data['rusher_player_name'] == player_name]['two_point_conv_result'] == 'success').sum()
    two_pt_rec_WN = (week_only_data[week_only_data['receiver_player_name'] == player_name]['two_point_conv_result'] == 'success').sum()

    total_P_YardsWN = week_only_data[week_only_data['passer_player_name'] == player_name]['passing_yards'].sum()
    total_R_YardsWN = week_only_data[week_only_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
    receiving_yardsWN = week_only_data[week_only_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
    receptionsWN = len(week_only_data[(week_only_data['receiver_player_name'] == player_name) & (week_only_data['complete_pass'] == 1)])
    interceptionsWN = week_only_data[week_only_data['passer_player_name'] == player_name]['interception'].sum()
    fumbles_lostWN = week_only_data[week_only_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
    pTdWN = week_only_data[week_only_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
    rtdWN = week_only_data[week_only_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
    recTdWN = week_only_data[week_only_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
    
    # Fantasty points from that week
    total_F_Points_WN = (total_P_YardsWN * .04) + (total_R_YardsWN * .1) + (receiving_yardsWN * .1) - (interceptionsWN * 2) + (pTdWN * 4) + (rtdWN * 6) + (recTdWN * 6) - (fumbles_lostWN * 2) + (receptionsWN) + (two_pt_rush_WN * 2) + (two_pt_pass_WN * 2) + (two_pt_rec_WN * 2)

    return total_F_Points_WN


all_data = pd.read_csv("../data/play_by_play_2025.csv", low_memory=False)
players = pd.read_csv("../data/offensive_players.csv", low_memory=False)

fantasy_points = []
new_dataframe = []

for row in players.itertuples(index=False):
    if row.position in ["QB", "WR", "RB", "TE", "FB"]:
        result = convert(row.first_name + " " + row.last_name, players)
        
        if result is None:
            continue
        
        abbr, team, pos = result
        fantasy_points_value = get_fantasy_sum(abbr, row.team, all_data)
        
        new_dataframe.append({
            'first_name': row.first_name,
            'last_name': row.last_name,
            'abbreviation': abbr,
            'team': row.team,
            'position': row.position,
            'fantasy_points': fantasy_points_value
        })

new_dataframe = pd.DataFrame(new_dataframe)
new_dataframe.to_csv("../data/fantasy_points.csv", index=False)