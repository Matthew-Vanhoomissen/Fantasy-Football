import pandas as pd

all_data = pd.read_csv("../../data/play_by_play_2025.csv", low_memory=False)
players = pd.concat([
    all_data['passer_player_name'],
    all_data['rusher_player_name'],
    all_data['receiver_player_name']
]).dropna().unique()

players_data = pd.DataFrame(players)
players_data.to_csv("../../data/players.csv", index=False)
