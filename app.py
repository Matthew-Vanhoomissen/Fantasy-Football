from flask import jsonify, request, Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["POST"])
def prediction():
    data = request.json
    print(data)
    return jsonify({
        "message": "Backend is working",
        "received": data
    })


if __name__ == "__main__":
    app.run(debug=True)