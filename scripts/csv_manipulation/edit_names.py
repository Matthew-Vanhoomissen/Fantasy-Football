import pandas as pd 


def edit_player_names() -> None:
    """
    Filters raw data from BALLDONTLIE API into necessary values
    to be utilized in the application. Filters for offensive players
    and corrects team name mismatches.

    """
    players = pd.read_csv("data/nfl_players.csv")

    new_dataframe = []
    for row in players.itertuples(index=False):
        if row.position in ["QB", "WR", "RB", "TE", "FB"]:
            team_name = row.team
            if team_name == "LAR":
                team_name = "LA"
            elif team_name == "WSH":
                team_name = "WAS"
            new_dataframe.append({
                'first_name': row.first_name,
                'last_name': row.last_name,
                'team': team_name,
                'position': row.position,
            })
    new_dataframe = pd.DataFrame(new_dataframe)
    new_dataframe.to_csv("data/offensive_players.csv", index=False)
