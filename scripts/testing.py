from scripts.input_collection.total_data_collection import get_prediction, CURRENT_SEASON
import pandas as pd


def main():
    name_file = pd.read_csv("data/offensive_players.csv", low_memory=False)
    all_data_current = pd.read_csv(f"data/play_by_play/play_by_play_{CURRENT_SEASON}.csv", low_memory=False)
    all_data_past = pd.read_csv(f"data/play_by_play/play_by_play_{CURRENT_SEASON - 1}.csv", low_memory=False)

    # Players sharing the abbreviated name 'J.Williams' should keep separate stats
    result, display1, display2, reason = get_prediction(
        "Jameson Williams", "Javonte Williams", 3, CURRENT_SEASON,
        name_file, all_data_current, all_data_past
    )

    val = {"data": result, "display1": display1, "display2": display2, "status": "success", "reason": reason}

    print(val['reason'])
    print(val['display1']['average_fantasy_points'])
    print(val['display2']['average_fantasy_points'])


if __name__ == "__main__":
    main()
