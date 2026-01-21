import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import jsonify, request, Flask
from flask_cors import CORS
from scripts.player_prediction import final_result
import pandas as pd


app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://fantasy-football-7w2a.vercel.app"
])

name_file = pd.read_csv("data/nfl_players.csv", low_memory=False)
all_data = pd.read_csv("data/play_by_play_2025.csv", low_memory=False)

def get_top_players_by_position(player_data, top_n=20):
    sorted_data = player_data.sort_values('fantasy_points', ascending=False)
    
    results = {
        'QB': sorted_data[sorted_data['position'] == 'QB'].head(top_n).to_dict('records'),
        'RB': sorted_data[sorted_data['position'] == 'RB'].head(top_n).to_dict('records'),
        'WR': sorted_data[sorted_data['position'] == 'WR'].head(top_n).to_dict('records'),
        'TE': sorted_data[sorted_data['position'] == 'TE'].head(top_n).to_dict('records'),
        'All': sorted_data.head(top_n).to_dict('records')
    }
    
    return results


def format_players(data):
    result = []
    for row in data.itertuples(index=False):
        result.append({
            'first_name': row.first_name,
            'last_name': row.last_name,
            'team': row.team,
            'position': row.position
        })
    return result

try:
    player_df = pd.read_csv('data/fantasy_points.csv')  
    TOP_PLAYERS_CACHE = get_top_players_by_position(player_df, top_n=20)
except Exception as e:
    print(f"Error loading player data: {e}")
    TOP_PLAYERS_CACHE = None


@app.route("/", methods=["POST"])
def prediction():
    data = request.json
    result, display1, display2, reason = final_result(data['player1'], data['player2'], data['week'], name_file, all_data)
    if result is None or display1 is None or display2 is None:
        return jsonify({"data": None, "display1": None, "display2": None,"status": "failed", "reason": reason})
    return jsonify({"data": result, "display1": display1, "display2": display2, "status": "success", "reason": None})


@app.route("/top-players", methods=["GET"])
def get_top_players():
    return jsonify({
        "status": "success",
        "data": TOP_PLAYERS_CACHE
    })


@app.route("/players", methods=["GET"])
def get_players():
    all_players_df = pd.read_csv('data/offensive_players.csv')
    result = format_players(all_players_df)

    return jsonify({
        "status": "success",
        "data": result
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)