# server.py - Flask server with authentication for the fuel station and fuel price application.
# Author: Marcin Kaminski

from datetime import date, datetime
from decimal import Decimal

import mysql.connector
from flask import Flask, request, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

import dbconfig as cfg
from fuelStationDAO import fuelStationDAO
from fuelPricesDAO import fuelPricesDAO
from fuelCalculationsDAO import fuelCalculationsDAO

app = Flask(__name__, static_url_path="", static_folder="staticpages")
app.config["SECRET_KEY"] = "change-this-secret-key-before-deployment"

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id, username):
        self.id = str(id)
        self.username = username


def get_db_connection():
    return mysql.connector.connect(**cfg.mysql)


@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(user["id"], user["username"])
        return None
    finally:
        cursor.close()
        connection.close()


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Authentication required"}), 401


def make_json_safe(value):
    """Convert database values such as Decimal/date into JSON-friendly values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: make_json_safe(item) for key, item in value.items()}
    return value


def get_required_query_param(name):
    value = request.args.get(name)
    if value is None or str(value).strip() == "":
        return None
    return str(value).strip()


@app.route("/")
def index():
    return app.send_static_file("index.html")


# -----------------------------
# Authentication endpoints
# -----------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    if user and check_password_hash(user["password_hash"], password):
        login_user(User(user["id"], user["username"]))
        return jsonify({"success": True, "username": user["username"]}), 200

    return jsonify({"error": "Invalid username or password"}), 401




@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 409

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash),
        )
        connection.commit()
        user_id = cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

    login_user(User(user_id, username))
    return jsonify({"success": True, "username": username}), 201


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True}), 200


@app.route("/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "username": current_user.username}), 200
    return jsonify({"authenticated": False, "username": None}), 200


# -----------------------------
# Fuel stations endpoints
# -----------------------------

@app.route("/fuel_stations", methods=["GET"])
def get_all_fuel_stations():
    fuel_stations = fuelStationDAO.getAll()
    return jsonify(make_json_safe(fuel_stations)), 200


@app.route("/fuel_stations/<int:id>", methods=["GET"])
def find_fuel_station_by_id(id):
    fuel_station = fuelStationDAO.findByID(id)
    if not fuel_station:
        return jsonify({"error": "Fuel station not found"}), 404
    return jsonify(make_json_safe(fuel_station)), 200


@app.route("/fuel_stations", methods=["POST"])
@login_required
def create_fuel_station():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    required_fields = ["name", "brand", "locality", "postcode"]
    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "":
            return jsonify({"error": f"{field} is required"}), 400

    fuel_station = {field: str(data.get(field)).strip() for field in required_fields}
    created = fuelStationDAO.create(fuel_station)
    return jsonify(make_json_safe(created)), 201


@app.route("/fuel_stations/<int:id>", methods=["PUT"])
@login_required
def update_fuel_station(id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    fuel_station = {}
    for field in ["name", "brand", "locality", "postcode"]:
        if field in data:
            value = str(data[field]).strip()
            if value == "":
                return jsonify({"error": f"{field} cannot be empty"}), 400
            fuel_station[field] = value

    if not fuel_station:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = fuelStationDAO.update(id, fuel_station)
    if not updated:
        return jsonify({"error": "Fuel station not found"}), 404
    return jsonify(make_json_safe(updated)), 200


@app.route("/fuel_stations/<int:id>", methods=["DELETE"])
@login_required
def delete_fuel_station(id):
    deleted = fuelStationDAO.delete(id)
    if not deleted:
        return jsonify({"error": "Fuel station not found"}), 404
    return jsonify({"success": True}), 200


# -----------------------------
# Fuel prices endpoints
# -----------------------------

@app.route("/fuel_prices", methods=["GET"])
def get_all_fuel_prices():
    fuel_prices = fuelPricesDAO.getAll()
    return jsonify(make_json_safe(fuel_prices)), 200


@app.route("/fuel_prices/<int:id>", methods=["GET"])
def find_fuel_price_by_id(id):
    fuel_price = fuelPricesDAO.findByID(id)
    if not fuel_price:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify(make_json_safe(fuel_price)), 200


@app.route("/fuel_prices", methods=["POST"])
@login_required
def create_fuel_price():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    required_fields = ["station_id", "petrol_95", "diesel", "lpg", "price_date"]
    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "":
            return jsonify({"error": f"{field} is required"}), 400

    fuel_price = {
        "station_id": data.get("station_id"),
        "petrol_95": str(data.get("petrol_95")).strip(),
        "diesel": str(data.get("diesel")).strip(),
        "lpg": str(data.get("lpg")).strip(),
        "price_date": str(data.get("price_date")).strip(),
    }
    created = fuelPricesDAO.create(fuel_price)
    return jsonify(make_json_safe(created)), 201


@app.route("/fuel_prices/<int:id>", methods=["PUT"])
@login_required
def update_fuel_price(id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    fuel_price = {}
    for field in ["station_id", "petrol_95", "diesel", "lpg", "price_date"]:
        if field in data:
            value = data[field]
            if value is None or str(value).strip() == "":
                return jsonify({"error": f"{field} cannot be empty"}), 400
            fuel_price[field] = value if field == "station_id" else str(value).strip()

    if not fuel_price:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = fuelPricesDAO.update(id, fuel_price)
    if not updated:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify(make_json_safe(updated)), 200


@app.route("/fuel_prices/<int:id>", methods=["DELETE"])
@login_required
def delete_fuel_price(id):
    deleted = fuelPricesDAO.delete(id)
    if not deleted:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify({"success": True}), 200


# -----------------------------
# Fuel calculations endpoints
# -----------------------------

@app.route("/fuel_calculations/latest_prices", methods=["GET"])
def get_latest_prices_by_date():
    price_date = get_required_query_param("price_date")
    if price_date is None:
        return jsonify({"error": "price_date query parameter is required"}), 400

    latest_prices = fuelCalculationsDAO.getLatestPricesByDate(price_date)
    return jsonify(make_json_safe(latest_prices)), 200


@app.route("/fuel_calculations/prices_by_locality", methods=["GET"])
def find_fuel_prices_by_locality_and_date():
    locality = get_required_query_param("locality")
    price_date = get_required_query_param("price_date")

    if locality is None:
        return jsonify({"error": "locality query parameter is required"}), 400
    if price_date is None:
        return jsonify({"error": "price_date query parameter is required"}), 400

    fuel_prices = fuelCalculationsDAO.findFuelPricesByLocalityAndDate(locality, price_date)
    return jsonify(make_json_safe(fuel_prices)), 200


@app.route("/fuel_calculations/cheapest_petrol_95", methods=["GET"])
def get_cheapest_petrol_95_by_date():
    price_date = get_required_query_param("price_date")
    if price_date is None:
        return jsonify({"error": "price_date query parameter is required"}), 400

    cheapest_fuel = fuelCalculationsDAO.getCheapestPetrol95ByDate(price_date)
    if not cheapest_fuel:
        return jsonify({"error": "Fuel price not found for given date"}), 404
    return jsonify(make_json_safe(cheapest_fuel)), 200


@app.route("/fuel_calculations/cheapest_diesel", methods=["GET"])
def get_cheapest_diesel_by_date():
    price_date = get_required_query_param("price_date")
    if price_date is None:
        return jsonify({"error": "price_date query parameter is required"}), 400

    cheapest_fuel = fuelCalculationsDAO.getCheapestDieselByDate(price_date)
    if not cheapest_fuel:
        return jsonify({"error": "Fuel price not found for given date"}), 404
    return jsonify(make_json_safe(cheapest_fuel)), 200


@app.route("/fuel_calculations/cheapest_lpg", methods=["GET"])
def get_cheapest_lpg_by_date():
    price_date = get_required_query_param("price_date")
    if price_date is None:
        return jsonify({"error": "price_date query parameter is required"}), 400

    cheapest_fuel = fuelCalculationsDAO.getCheapestLpgByDate(price_date)
    if not cheapest_fuel:
        return jsonify({"error": "Fuel price not found for given date"}), 404
    return jsonify(make_json_safe(cheapest_fuel)), 200


@app.route("/fuel_calculations/average_petrol_95_by_day", methods=["GET"])
def get_average_petrol_95_by_day():
    average_prices = fuelCalculationsDAO.getAveragePetrol95ByDay()
    return jsonify(make_json_safe(average_prices)), 200


@app.route("/fuel_calculations/average_diesel_by_day", methods=["GET"])
def get_average_diesel_by_day():
    average_prices = fuelCalculationsDAO.getAverageDieselByDay()
    return jsonify(make_json_safe(average_prices)), 200


@app.route("/fuel_calculations/average_lpg_by_day", methods=["GET"])
def get_average_lpg_by_day():
    average_prices = fuelCalculationsDAO.getAverageLpgByDay()
    return jsonify(make_json_safe(average_prices)), 200


@app.route("/fuel_calculations/average_all_fuel_types_by_day", methods=["GET"])
def get_average_all_fuel_types_by_day():
    average_prices = fuelCalculationsDAO.getAverageAllFuelTypesByDay()
    return jsonify(make_json_safe(average_prices)), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
