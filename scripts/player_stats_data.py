import pandas as pd
from target_percentage import get_percentage
from target_percentage import get_week_percentage


def get_player_data(player_name, team_name, pdp, all_stats): 

    team_name3 = pdp['posteam'].mode()[0]

    # Most frequent opponent when that team was on offense
    opponent_team3 = pdp[pdp['posteam'] == team_name]['defteam'].mode()[0]
    print(team_name3)
    print(opponent_team3)

    # Make array
    player_stats = []

    total_P_Yards = pdp[pdp['passer_player_name'] == player_name]['passing_yards'].sum()
    print("Total passing yards: ")
    print(total_P_Yards)

    total_R_Yards = pdp[pdp['rusher_player_name'] == player_name]['rushing_yards'].sum()
    print(f"Total rushing yards: {total_R_Yards}")

    games_played = pdp['week'].nunique()
    print(f"Games played: {games_played}")

    average_P_Yards = total_P_Yards/games_played
    average_R_Yards = total_R_Yards/games_played
    print(f"Average yards per game: {average_P_Yards}")
    print(f"Average rushing yards: {average_R_Yards}")

    receptions = len(pdp[(pdp['receiver_player_name'] == player_name) & (pdp['receiving_yards'] > 0)])
    print(f"Total receptions: {receptions}")

    receiving_yards = pdp[pdp['receiver_player_name'] == player_name]['receiving_yards'].sum()
    print(f"Total receiving yards: {receiving_yards}")
    average_rec_yards = receiving_yards / games_played

    interceptions = pdp[pdp['passer_player_name'] == player_name]['interception'].sum()
    print(f"Total interceptions: {interceptions}")

    fumbles_lost = pdp[pdp['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
    print(f"Fumbles lost: {fumbles_lost}")

    pTd = pdp[pdp['passer_player_name'] == player_name]['pass_touchdown'].sum()
    print(pTd)
    rtd = pdp[pdp['rusher_player_name'] == player_name]['rush_touchdown'].sum()
    print(rtd)
    recTd = pdp[pdp['receiver_player_name'] == player_name]['pass_touchdown'].sum()
    print(recTd)

    print(f"Total tds: {pTd + rtd + recTd}")

    total_F_Points = (total_P_Yards * .04) + (total_R_Yards * .1) + (receiving_yards * .1) - (interceptions * 2) + (pTd * 4) + (rtd * 6) + (recTd * 6) - (fumbles_lost * 2) + (receptions)
    average_F_Points = total_F_Points / games_played
    print(f"Total fantasy points: {total_F_Points}, Average points per game: {average_F_Points}")

    print("")
    # fantasy scoring for a single week
    weeks = sorted(pdp['week'].unique())

    # Arrays to store week difference
    positive_difference = []
    negative_difference = []
    boom_games = 0
    bust_games = 0
    # Goes through each week to find that weeks player data
    for week_num in weeks:
        week_data = pdp[pdp['week'] == week_num]
        
        total_P_YardsW = week_data[week_data['passer_player_name'] == player_name]['passing_yards'].sum()
        total_R_YardsW = week_data[week_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
        receiving_yardsW = week_data[week_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
        receptionsW = len(week_data[(week_data['receiver_player_name'] == player_name) & (week_data['receiving_yards'] > 0)])
        interceptionsW = week_data[week_data['passer_player_name'] == player_name]['interception'].sum()
        fumbles_lostW = week_data[week_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
        pTdW = week_data[week_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
        rtdW = week_data[week_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
        recTdW = week_data[week_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
        
        # Fantasty points from that week
        total_F_Points_W = (total_P_YardsW * .04) + (total_R_YardsW * .1) + (receiving_yardsW * .1) - (interceptionsW * 2) + (pTdW * 4) + (rtdW * 6) + (recTdW * 6) - (fumbles_lostW * 2) + (receptionsW)
        
        print(f"Week {week_num}: {total_F_Points_W} fantasy points")

        # difference of that week from average
        week_difference = ((total_F_Points_W - average_F_Points) / average_F_Points)
        week_diff_amount = (total_F_Points_W - average_F_Points)

        # if over or under a threshhold add to array that stores the percentage it went over or under
        if week_diff_amount > 10: 
            boom_games = boom_games + 1
            positive_difference.append(week_difference)
        elif week_diff_amount < -10: 
            bust_games = bust_games + 1
            negative_difference.append(week_difference)

    # Averages out how much it went over or under for those games
    pos_total = 0
    for num in positive_difference: 
        pos_total = pos_total + num

    pos_average = ((pos_total / len(positive_difference)) * 100) if boom_games else 0
    print(f"Of all games, the player boomed: {boom_games} and went over the average by: {pos_average}") if boom_games else 0

    neg_total = 0
    for num in negative_difference:
        neg_total = neg_total + (-num)

    neg_average = ((neg_total / len(negative_difference)) * 100) if bust_games else 0
    print(f"Of all games, the player bust: {bust_games} and went under the average by: {neg_average}") if bust_games else 0

    # if boom and bust games are not zero, calculate the boom/bust points as the 
    # multiplication of the average bust/boom percentage and the average fantasy points
    if boom_games > 0:
        boom_points = ((pos_average / 100) + 1) * average_F_Points
    else: 
        boom_points = average_F_Points

    if bust_games > 0:
        bust_points = ((neg_average / 100)) * average_F_Points
    else: 
        bust_points = average_F_Points

    print(f"Prediction: --bust({bust_games / games_played}): {bust_points} -- average points: {average_F_Points} -- boom({boom_games / games_played}): {boom_points}")

    # compare with last 3 game average
    last_three_weeks = 0
    for week in weeks[-3:]:
        week_data = pdp[pdp['week'] == week]

        total_P_YardsW = week_data[week_data['passer_player_name'] == player_name]['passing_yards'].sum()
        total_R_YardsW = week_data[week_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
        receiving_yardsW = week_data[week_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
        receptionsW = len(week_data[(week_data['receiver_player_name'] == player_name) & (week_data['receiving_yards'] > 0)])
        interceptionsW = week_data[week_data['passer_player_name'] == player_name]['interception'].sum()
        fumbles_lostW = week_data[week_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
        pTdW = week_data[week_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
        rtdW = week_data[week_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
        recTdW = week_data[week_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
        
        # Fantasty points from that week
        total_F_Points_W = (total_P_YardsW * .04) + (total_R_YardsW * .1) + (receiving_yardsW * .1) - (interceptionsW * 2) + (pTdW * 4) + (rtdW * 6) + (recTdW * 6) - (fumbles_lostW * 2) + (receptionsW)
        last_three_weeks = last_three_weeks + total_F_Points_W
        print(f"Week {week}: {total_F_Points_W} fantasy points")

    three_week_average = last_three_weeks / 3
    print(f"The total average is {average_F_Points} points, over the past 3 weeks the average is {three_week_average} points")
    percentages = get_percentage(team_name, player_name, all_stats)

    # collect data
    player_stats.append({
        'team_name': team_name,
        'player_name': player_name,
        'receptions_avg': receptions / games_played,
        'average_passing_yards': average_P_Yards,
        'average_rushing_yards': average_R_Yards,
        'average_recieving_yards': average_rec_yards,
        'passing_tds_avg': pTd / games_played,
        'rushing_tds_avg': rtd / games_played,
        'recieving_tds_avg': recTd / games_played,
        'average_fantasy_points': total_F_Points / games_played,
        'bust_percent': bust_games / games_played,
        'bust_points_average': bust_points,
        'boom_percent': boom_games / games_played,
        'boom_points_average': boom_points,
        'last_three_weeks_diff': three_week_average - average_F_Points,
    })

    player_stats_dataframe = pd.DataFrame(player_stats)

    return pd.merge(player_stats_dataframe, percentages, how="left")


def get_player_week_data(player_name, team_name, team_data, all_stats, week_input): 
    week_only_data = team_data[team_data['week'] == week_input]

    total_P_YardsWN = week_only_data[week_only_data['passer_player_name'] == player_name]['passing_yards'].sum()
    total_R_YardsWN = week_only_data[week_only_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
    receiving_yardsWN = week_only_data[week_only_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
    receptionsWN = len(week_only_data[(week_only_data['receiver_player_name'] == player_name) & (week_only_data['receiving_yards'] > 0)])
    interceptionsWN = week_only_data[week_only_data['passer_player_name'] == player_name]['interception'].sum()
    fumbles_lostWN = week_only_data[week_only_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
    pTdWN = week_only_data[week_only_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
    rtdWN = week_only_data[week_only_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
    recTdWN = week_only_data[week_only_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
    
    # Fantasty points from that week
    total_F_Points_WN = (total_P_YardsWN * .04) + (total_R_YardsWN * .1) + (receiving_yardsWN * .1) - (interceptionsWN * 2) + (pTdWN * 4) + (rtdWN * 6) + (recTdWN * 6) - (fumbles_lostWN * 2) + (receptionsWN)

    pdp = team_data[team_data['week'] < week_input]

    # Most frequent opponent when that team was on offense

    # Make array
    player_stats = []

    total_P_Yards = pdp[pdp['passer_player_name'] == player_name]['passing_yards'].sum()

    total_R_Yards = pdp[pdp['rusher_player_name'] == player_name]['rushing_yards'].sum()

    games_played = pdp['week'].nunique()
    if games_played == 0:
        return None

    average_P_Yards = total_P_Yards/games_played
    average_R_Yards = total_R_Yards/games_played

    receptions = len(pdp[(pdp['receiver_player_name'] == player_name) & (pdp['receiving_yards'] > 0)])

    receiving_yards = pdp[pdp['receiver_player_name'] == player_name]['receiving_yards'].sum()

    average_rec_yards = receiving_yards / games_played

    interceptions = pdp[pdp['passer_player_name'] == player_name]['interception'].sum()

    fumbles_lost = pdp[pdp['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()

    pTd = pdp[pdp['passer_player_name'] == player_name]['pass_touchdown'].sum()
  
    rtd = pdp[pdp['rusher_player_name'] == player_name]['rush_touchdown'].sum()

    recTd = pdp[pdp['receiver_player_name'] == player_name]['pass_touchdown'].sum()

    total_F_Points = (total_P_Yards * .04) + (total_R_Yards * .1) + (receiving_yards * .1) - (interceptions * 2) + (pTd * 4) + (rtd * 6) + (recTd * 6) - (fumbles_lost * 2) + (receptions)
    average_F_Points = total_F_Points / games_played

    # fantasy scoring for a single week
    weeks = sorted(pdp['week'].unique())

    # Arrays to store week difference
    positive_difference = []
    negative_difference = []
    boom_games = 0
    bust_games = 0
    # Goes through each week to find that weeks player data
    for week_num in weeks:
        week_data = pdp[pdp['week'] == week_num]
        
        total_P_YardsW = week_data[week_data['passer_player_name'] == player_name]['passing_yards'].sum()
        total_R_YardsW = week_data[week_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
        receiving_yardsW = week_data[week_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
        receptionsW = len(week_data[(week_data['receiver_player_name'] == player_name) & (week_data['receiving_yards'] > 0)])
        interceptionsW = week_data[week_data['passer_player_name'] == player_name]['interception'].sum()
        fumbles_lostW = week_data[week_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
        pTdW = week_data[week_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
        rtdW = week_data[week_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
        recTdW = week_data[week_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
        
        # Fantasty points from that week
        total_F_Points_W = (total_P_YardsW * .04) + (total_R_YardsW * .1) + (receiving_yardsW * .1) - (interceptionsW * 2) + (pTdW * 4) + (rtdW * 6) + (recTdW * 6) - (fumbles_lostW * 2) + (receptionsW)
        
        # difference of that week from average
        if average_F_Points == 0:
            week_difference = 0
        else:
            week_difference = ((total_F_Points_W - average_F_Points) / average_F_Points)
        week_diff_amount = (total_F_Points_W - average_F_Points)

        # if over or under a threshhold add to array that stores the percentage it went over or under
        if week_diff_amount > 10: 
            boom_games = boom_games + 1
            positive_difference.append(week_difference)
        elif week_diff_amount < -10: 
            bust_games = bust_games + 1
            negative_difference.append(week_difference)

    # Averages out how much it went over or under for those games
    pos_total = 0
    for num in positive_difference: 
        pos_total = pos_total + num

    pos_average = ((pos_total / len(positive_difference)) * 100) if boom_games else 0

    neg_total = 0
    for num in negative_difference:
        neg_total = neg_total + (-num)

    neg_average = ((neg_total / len(negative_difference)) * 100) if bust_games else 0

    # if boom and bust games are not zero, calculate the boom/bust points as the 
    # multiplication of the average bust/boom percentage and the average fantasy points
    if boom_games > 0:
        boom_points = ((pos_average / 100) + 1) * average_F_Points
    else: 
        boom_points = average_F_Points

    if bust_games > 0:
        bust_points = ((neg_average / 100)) * average_F_Points
    else: 
        bust_points = average_F_Points

    # compare with last 3 game average
    last_three_weeks = 0
    weeks_counted = 0
    for week in weeks[-3:]:
        week_data = pdp[pdp['week'] == week]

        total_P_YardsW = week_data[week_data['passer_player_name'] == player_name]['passing_yards'].sum()
        total_R_YardsW = week_data[week_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
        receiving_yardsW = week_data[week_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
        receptionsW = len(week_data[(week_data['receiver_player_name'] == player_name) & (week_data['receiving_yards'] > 0)])
        interceptionsW = week_data[week_data['passer_player_name'] == player_name]['interception'].sum()
        fumbles_lostW = week_data[week_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
        pTdW = week_data[week_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
        rtdW = week_data[week_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
        recTdW = week_data[week_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
        
        # Fantasty points from that week
        total_F_Points_W = (total_P_YardsW * .04) + (total_R_YardsW * .1) + (receiving_yardsW * .1) - (interceptionsW * 2) + (pTdW * 4) + (rtdW * 6) + (recTdW * 6) - (fumbles_lostW * 2) + (receptionsW)
        last_three_weeks = last_three_weeks + total_F_Points_W
        weeks_counted += 1

    three_week_average = last_three_weeks / weeks_counted if weeks_counted > 0 else average_F_Points
    percentages = get_week_percentage(team_name, player_name, all_stats, week_input)

    # collect data
    player_stats.append({
        'week': week_input,
        'team_name': team_name,
        'player_name': player_name,
        'receptions_avg': receptions / games_played,
        'average_passing_yards': average_P_Yards,
        'average_rushing_yards': average_R_Yards,
        'average_recieving_yards': average_rec_yards,
        'passing_tds_avg': pTd / games_played,
        'rushing_tds_avg': rtd / games_played,
        'recieving_tds_avg': recTd / games_played,
        'average_fantasy_points': total_F_Points / games_played,
        'week_fantasy_points': total_F_Points_WN,
        'bust_percent': bust_games / games_played,
        'bust_points_average': bust_points,
        'boom_percent': boom_games / games_played,
        'boom_points_average': boom_points,
        'last_three_weeks_diff': three_week_average - average_F_Points,
    })

    player_stats_dataframe = pd.DataFrame(player_stats)

    return pd.merge(player_stats_dataframe, percentages, how="left")


def get_player_team(all_data, player_name):
    # Find plays where the player was involved
    player_plays = all_data[
        (all_data['passer_player_name'] == player_name) |
        (all_data['rusher_player_name'] == player_name) |
        (all_data['receiver_player_name'] == player_name)
    ]
    
    # Get the player's team (posteam - team on offense when player was involved)
    player_team = player_plays['posteam'].mode()[0] if len(player_plays) > 0 else None
    
    return player_team


def get_opponent_team(all_data, offensive_team_name, week):
    # Filter data for the specific week and offensive team
    week_data = all_data[
        (all_data['week'] == week) &
        (all_data['posteam'] == offensive_team_name)
    ]
    
    # Get the opponent team (defteam when team was on offense)
    opponent_team = week_data['defteam'].mode()[0] if len(week_data) > 0 else None
    
    return opponent_team