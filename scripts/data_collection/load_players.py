import pandas as pd


def main(
    year: int
) -> None:
    """
    Parses every player name that has participated so far in the input season.
    Utilized through training data generation to get all unique player inputs.

    """
    all_data = pd.read_csv(f"data/play_by_play/play_by_play_{year}.csv", low_memory=False)
    players = pd.concat([
        all_data['passer_player_name'],
        all_data['rusher_player_name'],
        all_data['receiver_player_name']
    ]).dropna().unique()

    players_data = pd.DataFrame(players)
    players_data.to_csv(f"data/player_names/players_{year}.csv", index=False)


if __name__ == "__main__":
    main(2021)
