import pandas as pd


def edit_player_names() -> None:
    """
    Filters raw roster data from nflverse into necessary values
    to be utilized in the application. Filters for offensive players
    on a current roster and keeps the GSIS ID for play-by-play lookups.

    """
    players = pd.read_csv("data/nfl_players.csv", low_memory=False)

    # Players without an ID cannot be matched to plays and released or
    # retired players are no longer on the listed team
    players = players[
        (players['position'].isin(["QB", "WR", "RB", "TE", "FB"])) &
        (~players['status'].isin(["CUT", "RET"])) &
        (players['gsis_id'].notna())
    ]

    new_dataframe = []
    for row in players.itertuples(index=False):
        # Split the commonly used full name (e.g. 'Matthew Stafford') rather than the
        # legal first name (e.g. 'John') so the frontend sends back the full name
        first_name, last_name = row.full_name.split(" ", 1)
        new_dataframe.append({
            'first_name': first_name,
            'last_name': last_name,
            'full_name': row.full_name,
            'team': row.team,
            'position': row.position,
            'gsis_id': row.gsis_id
        })
    new_dataframe = pd.DataFrame(new_dataframe)
    new_dataframe.to_csv("data/offensive_players.csv", index=False)
