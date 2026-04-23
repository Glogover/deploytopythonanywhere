# server.py - This file contains the Flask server implementation for the fuel station and fuel price application.
# Author: Marcin Kaminski

from flask import Flask, request, jsonify
from fuelStationDAO import fuelStationDAO
from fuelPricesDAO import fuelPricesDAO

app = Flask(__name__, static_url_path="", static_folder="staticpages")


@app.route("/")
def index():
    return app.send_static_file("index.html")


# -----------------------------
# Fuel stations endpoints
# -----------------------------

@app.route("/fuel_stations", methods=["GET"])
def get_all_fuel_stations():
    fuel_stations = fuelStationDAO.getAll()
    return jsonify(fuel_stations), 200


@app.route("/fuel_stations/<int:id>", methods=["GET"])
def find_fuel_station_by_id(id):
    fuel_station = fuelStationDAO.findByID(id)
    if not fuel_station:
        return jsonify({"error": "Fuel station not found"}), 404
    return jsonify(fuel_station), 200


@app.route("/fuel_stations", methods=["POST"])
def create_fuel_station():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name")
    brand = data.get("brand")
    locality = data.get("locality")
    postcode = data.get("postcode")

    if name is None or str(name).strip() == "":
        return jsonify({"error": "name is required"}), 400
    if brand is None or str(brand).strip() == "":
        return jsonify({"error": "brand is required"}), 400
    if locality is None or str(locality).strip() == "":
        return jsonify({"error": "locality is required"}), 400
    if postcode is None or str(postcode).strip() == "":
        return jsonify({"error": "postcode is required"}), 400

    fuel_station = {
        "name": str(name).strip(),
        "brand": str(brand).strip(),
        "locality": str(locality).strip(),
        "postcode": str(postcode).strip(),
    }

    created = fuelStationDAO.create(fuel_station)
    return jsonify(created), 201


@app.route("/fuel_stations/<int:id>", methods=["PUT"])
def update_fuel_station(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    fuel_station = {}

    if "name" in data:
        name = str(data["name"]).strip()
        if name == "":
            return jsonify({"error": "name cannot be empty"}), 400
        fuel_station["name"] = name

    if "brand" in data:
        brand = str(data["brand"]).strip()
        if brand == "":
            return jsonify({"error": "brand cannot be empty"}), 400
        fuel_station["brand"] = brand

    if "locality" in data:
        locality = str(data["locality"]).strip()
        if locality == "":
            return jsonify({"error": "locality cannot be empty"}), 400
        fuel_station["locality"] = locality

    if "postcode" in data:
        postcode = str(data["postcode"]).strip()
        if postcode == "":
            return jsonify({"error": "postcode cannot be empty"}), 400
        fuel_station["postcode"] = postcode

    if not fuel_station:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = fuelStationDAO.update(id, fuel_station)
    if not updated:
        return jsonify({"error": "Fuel station not found"}), 404

    return jsonify(updated), 200


@app.route("/fuel_stations/<int:id>", methods=["DELETE"])
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
    return jsonify(fuel_prices), 200


@app.route("/fuel_prices/<int:id>", methods=["GET"])
def find_fuel_price_by_id(id):
    fuel_price = fuelPricesDAO.findByID(id)
    if not fuel_price:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify(fuel_price), 200


@app.route("/fuel_prices", methods=["POST"])
def create_fuel_price():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    station_id = data.get("station_id")
    petrol_95 = data.get("petrol_95")
    diesel = data.get("diesel")
    lpg = data.get("lpg")
    price_date = data.get("price_date")

    if station_id is None:
        return jsonify({"error": "station_id is required"}), 400
    if petrol_95 is None or str(petrol_95).strip() == "":
        return jsonify({"error": "petrol_95 is required"}), 400
    if diesel is None or str(diesel).strip() == "":
        return jsonify({"error": "diesel is required"}), 400
    if lpg is None or str(lpg).strip() == "":
        return jsonify({"error": "lpg is required"}), 400
    if price_date is None or str(price_date).strip() == "":
        return jsonify({"error": "price_date is required"}), 400

    fuel_price = {
        "station_id": station_id,
        "petrol_95": str(petrol_95).strip(),
        "diesel": str(diesel).strip(),
        "lpg": str(lpg).strip(),
        "price_date": str(price_date).strip(),
    }

    created = fuelPricesDAO.create(fuel_price)
    return jsonify(created), 201


@app.route("/fuel_prices/<int:id>", methods=["PUT"])
def update_fuel_price(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    fuel_price = {}

    if "station_id" in data:
        station_id = data["station_id"]
        if station_id is None:
            return jsonify({"error": "station_id cannot be empty"}), 400
        fuel_price["station_id"] = station_id

    if "petrol_95" in data:
        petrol_95 = str(data["petrol_95"]).strip()
        if petrol_95 == "":
            return jsonify({"error": "petrol_95 cannot be empty"}), 400
        fuel_price["petrol_95"] = petrol_95

    if "diesel" in data:
        diesel = str(data["diesel"]).strip()
        if diesel == "":
            return jsonify({"error": "diesel cannot be empty"}), 400
        fuel_price["diesel"] = diesel

    if "lpg" in data:
        lpg = str(data["lpg"]).strip()
        if lpg == "":
            return jsonify({"error": "lpg cannot be empty"}), 400
        fuel_price["lpg"] = lpg

    if "price_date" in data:
        price_date = str(data["price_date"]).strip()
        if price_date == "":
            return jsonify({"error": "price_date cannot be empty"}), 400
        fuel_price["price_date"] = price_date

    if not fuel_price:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = fuelPricesDAO.update(id, fuel_price)
    if not updated:
        return jsonify({"error": "Fuel price not found"}), 404

    return jsonify(updated), 200


@app.route("/fuel_prices/<int:id>", methods=["DELETE"])
def delete_fuel_price(id):
    deleted = fuelPricesDAO.delete(id)
    if not deleted:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify({"success": True}), 200




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
