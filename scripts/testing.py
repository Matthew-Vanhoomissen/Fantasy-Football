from scripts.input_collection.total_data_collection import get_prediction
import pandas as pd
from flask import jsonify, request, Flask
from flask_cors import CORS


def main():
    name_file = pd.read_csv("data/nfl_players.csv", low_memory=False)
    all_data = pd.read_csv("data/play_by_play/play_by_play_2025.csv", low_memory=False)

    result, display1, display2, reason = get_prediction("Dontayvion Wicks", "Ja'Marr Chase", 18, name_file, all_data)

    val = {"data": result, "display1": display1, "display2": display2, "status": "success", "reason": reason}

    print(val['display1']['epa_per_pass'])

if __name__ == "__main__":
    main()
