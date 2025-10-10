import pandas as pd

pdp = pd.read_csv("../data/J.Allen_data_2025.csv", low_memory=False)
print("Josh Allen stats")

total_P_Yards = pdp['passing_yards'].sum()
print("Total passing yards: ")
print(total_P_Yards)

total_R_Yards = pdp[pdp['rusher_player_name'] == 'J.Allen']['rushing_yards'].sum()
print(f"Total rushing yards: {total_R_Yards}")

games_played = pdp['week'].nunique()
print(f"Games played: {games_played}")

average_P_Yards = total_P_Yards/games_played
average_R_Yards = total_R_Yards/games_played
print(f"Average yards per game: {average_P_Yards}")
print(f"Average rushing yards: {average_R_Yards}")

receiving_yards = pdp[pdp['receiver_player_name'] == 'J.Allen']['receiving_yards'].sum()
print(f"Total receiving yards: {receiving_yards}")

interceptions = pdp['interception'].sum()
print(f"Total interceptions: {interceptions}")

fumbles_lost = pdp[pdp['fumbled_1_player_name'] == 'J.Allen']['fumble_lost'].sum()
print(f"Fumbles lost: {fumbles_lost}")

pTd = pdp['pass_touchdown'].sum()
print(pTd)
rtd = pdp[pdp['rusher_player_name'] == 'J.Allen']['rush_touchdown'].sum()
print(rtd)

print(f"Total tds: {pTd + rtd}")

total_F_Points = (total_P_Yards * .04) + (total_R_Yards * .1) + (receiving_yards * .1) - (interceptions * 2) + (pTd * 4) + (rtd * 6) - (fumbles_lost * 2)
average_F_Points = total_F_Points / games_played
print(f"Total fantasy points: {total_F_Points}, Average points per game: {average_F_Points}")

print("")
# fantasy scoring for a single week
weeks = sorted(pdp['week'].unique())

for week_num in weeks:
    week_data = pdp[pdp['week'] == week_num]
    
    total_P_Yards = week_data['passing_yards'].sum()
    total_R_Yards = week_data[week_data['rusher_player_name'] == 'J.Allen']['rushing_yards'].sum()
    receiving_yards = week_data[week_data['receiver_player_name'] == 'J.Allen']['receiving_yards'].sum()
    interceptions = week_data['interception'].sum()
    fumbles_lost = week_data[week_data['fumbled_1_player_name'] == 'J.Allen']['fumble_lost'].sum()
    pTd = week_data['pass_touchdown'].sum()
    rtd = week_data[week_data['rusher_player_name'] == 'J.Allen']['rush_touchdown'].sum()
    
    total_F_Points = (total_P_Yards * .04) + (total_R_Yards * .1) + (receiving_yards * .1) - (interceptions * 2) + (pTd * 4) + (rtd * 6) - (fumbles_lost * 2)
    
    print(f"Week {week_num}: {total_F_Points} fantasy points")