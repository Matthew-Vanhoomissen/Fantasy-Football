import pandas as pd

# ============================================================
# FILTERED DATAFRAME BUILDER
# ============================================================
def create_csvs_offense(
    pbp: pd.DataFrame,
    player_id: str,
    offensive_team_name: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Given historic play-by-play data, filter DataFrame based on team and player ID.

    """

    # filter the dataframe
    offensive_team_data = pbp[(pbp['home_team'] == offensive_team_name) | (pbp['away_team'] == offensive_team_name)]

    # filter for player
    player_data = pbp[
        (pbp['passer_player_id'] == player_id) |
        (pbp['rusher_player_id'] == player_id) |
        (pbp['receiver_player_id'] == player_id)
    ]

    return offensive_team_data, player_data


def create_csvs_defense(
    pbp: pd.DataFrame,
    defense_team_name: str
) -> pd.DataFrame:
    """
    Given historic play-by-play data, filter DataFrame based on defensive team name.

    """

    defensive_team_data = pbp[(pbp['home_team'] == defense_team_name) | (pbp['away_team'] == defense_team_name)]

    return defensive_team_data

# ============================================================
# FORMATTING HELPER METHODS
# ============================================================
def return_opponent(
    team: str,
    week: int,
    season: int
) -> None | str:
    """
    Parses future schedule to give accurate matchups for that week

    """
    schedule = pd.read_csv(f"data/schedule_{season}.csv")

    schedule = schedule[schedule["week"] == week]

    away = schedule[schedule['away_team'] == team]
    if not away.empty:
        return (away.iloc[0])['home_team']
    home = schedule[schedule['home_team'] == team]
    if not home.empty:
        return (home.iloc[0])['away_team']

    return None


def convert(
    name: str,          # Full name of player
    file: pd.DataFrame  # Stored name file
) -> tuple[None, None, None] | tuple[str, str, str]:
    """
    Critical lookup method that converts a full name to the GSIS player ID that
    appears in play-by-play data. The ID is unique to each player, which avoids
    collisions between players sharing an abbreviated name (e.g. 'J.Williams')
    """
    player = file[file['full_name'] == name]
    if player.empty:
        return None, None, None
    player = player.iloc[0]

    return player['gsis_id'], player['team'], player['position']
