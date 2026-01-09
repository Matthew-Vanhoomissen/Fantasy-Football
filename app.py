import os
import sys

# Change working directory to the base folder (where app.py is)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import jsonify, request, Flask
from flask_cors import CORS
from scripts.player_prediction import final_result


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["POST"])
def prediction():
    data = request.json
    result, display1, display2, = final_result(data['player1'], data['player2'])
    if result is None:
        return jsonify({"data": None, "display1": None, "display2": None,"status": "failed"})
    return jsonify({"data": result, "display1": display1, "display2": display2, "status": "success"})


if __name__ == "__main__":
    app.run(debug=True)