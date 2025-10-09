import pandas as pd 

# load csv file
team_data = pd.read_csv("../data/team_data_2025.csv", low_memory=False)

team_name = "GB"

offensive_plays = team_data[
    (team_data['posteam'] == team_name) & 
    (team_data['play_type'].isin(['pass', 'run'])) &
    (team_data['kickoff_attempt'] == 0) &
    (team_data['extra_point_attempt'] == 0) &
    (team_data['epa'].notna()) &
    (team_data['qb_kneel'] == 0) &
    (team_data['qb_spike'] == 0) &
    (team_data['penalty'] == 0) & 
    (team_data['two_point_attempt'] == 0)
]

total_epa = offensive_plays['epa'].sum()
total_plays = len(offensive_plays)
epa_per_play = total_epa / total_plays

print(f"Total offensive EPA: {total_epa}")
print(f"Total plays: {total_plays}")
print(f"EPA per play: {epa_per_play}")
