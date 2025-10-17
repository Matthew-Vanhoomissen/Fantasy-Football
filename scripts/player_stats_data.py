import pandas as pd
from target_percentage import get_percentage

pdp = pd.read_csv("../data/player1_data_2025.csv", low_memory=False)
print("Player stats")

player_name = 'T.Kraft'

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
    
    total_P_Yards = week_data[week_data['passer_player_name'] == player_name]['passing_yards'].sum()
    total_R_Yards = week_data[week_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
    receiving_yards = week_data[week_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
    receptions = len(week_data[(week_data['receiver_player_name'] == player_name) & (week_data['receiving_yards'] > 0)])
    interceptions = week_data[week_data['passer_player_name'] == player_name]['interception'].sum()
    fumbles_lost = week_data[week_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
    pTd = week_data[week_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
    rtd = week_data[week_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
    recTd = week_data[week_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
    
    # Fantasty points from that week
    total_F_Points_W = (total_P_Yards * .04) + (total_R_Yards * .1) + (receiving_yards * .1) - (interceptions * 2) + (pTd * 4) + (rtd * 6) + (recTd * 6) - (fumbles_lost * 2) + (receptions)
    
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
print(f"Of all games, the player bust: {bust_games} and went over the average by: {neg_average}") if bust_games else 0

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

    total_P_Yards = week_data[week_data['passer_player_name'] == player_name]['passing_yards'].sum()
    total_R_Yards = week_data[week_data['rusher_player_name'] == player_name]['rushing_yards'].sum()
    receiving_yards = week_data[week_data['receiver_player_name'] == player_name]['receiving_yards'].sum()
    receptions = len(week_data[(week_data['receiver_player_name'] == player_name) & (week_data['receiving_yards'] > 0)])
    interceptions = week_data[week_data['passer_player_name'] == player_name]['interception'].sum()
    fumbles_lost = week_data[week_data['fumbled_1_player_name'] == player_name]['fumble_lost'].sum()
    pTd = week_data[week_data['passer_player_name'] == player_name]['pass_touchdown'].sum()
    rtd = week_data[week_data['rusher_player_name'] == player_name]['rush_touchdown'].sum()
    recTd = week_data[week_data['receiver_player_name'] == player_name]['pass_touchdown'].sum()
    
    # Fantasty points from that week
    total_F_Points_W = (total_P_Yards * .04) + (total_R_Yards * .1) + (receiving_yards * .1) - (interceptions * 2) + (pTd * 4) + (rtd * 6) + (recTd * 6) - (fumbles_lost * 2) + (receptions)
    last_three_weeks = last_three_weeks + total_F_Points_W
    print(f"Week {week}: {total_F_Points_W} fantasy points")

three_week_average = last_three_weeks / 3
print(f"The total average is {average_F_Points} points, over the past 3 weeks the average is {three_week_average} points")
get_percentage("GB", "T.Kraft")
