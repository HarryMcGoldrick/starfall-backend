from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from controllers.meteorites_controller import meteorite_controller
from controllers.user_controller import user_controller

app = Flask(__name__)
app.register_blueprint(meteorite_controller)
app.register_blueprint(user_controller)
CORS(app)

@app.route("/", methods=["GET"])
def index():
	return make_response("<h1>Star fall!</h1>", 200)

if __name__ == "__main__":
	app.run(debug=True)