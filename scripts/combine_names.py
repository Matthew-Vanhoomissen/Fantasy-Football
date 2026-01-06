import pandas as pd 

full_name = pd.read_csv("../data/nfl_players.csv", low_memory=False)

full_name["abbr"] = full_name["first_name"].str[0] + "." + full_name["last_name"]