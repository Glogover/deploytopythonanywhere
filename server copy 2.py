from flask import Flask, request, jsonify
from fuelPricesDAO import fuelPricesDAO

app = Flask(__name__, static_url_path="", static_folder="staticpages")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/fuel_prices", methods=["GET"])
def get_all():
    fuel_prices = fuelPricesDAO.getAll()
    return jsonify(fuel_prices), 200


@app.route("/fuel_prices/<int:id>", methods=["GET"])
def find_by_id(id):
    fuel_price = fuelPricesDAO.findByID(id)
    if not fuel_price:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify(fuel_price), 200


@app.route("/fuel_prices", methods=["POST"])
def create():
    data = request.get_json()

    if not data:
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
    if price_date is None:
        return jsonify({"error": "price_date is required"}), 400

    fuel_price = {
        "station_id": station_id,
        "petrol_95": str(petrol_95).strip(),
        "diesel": str(diesel).strip(),
        "lpg": str(lpg).strip(),
        "price_date": price_date
    }

    created = fuelPricesDAO.create(fuel_price)
    return jsonify(created), 201


@app.route("/fuel_prices/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json()

    if not data:
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
        price_date = data["price_date"]
        if price_date is None:
            return jsonify({"error": "price_date cannot be empty"}), 400
        fuel_price["price_date"] = price_date

    if not fuel_price:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = fuelPricesDAO.update(id, fuel_price)
    if not updated:
        return jsonify({"error": "Fuel price not found"}), 404

    return jsonify(updated), 200


@app.route("/fuel_prices/<int:id>", methods=["DELETE"])
def delete(id):
    deleted = fuelPricesDAO.delete(id)
    if not deleted:
        return jsonify({"error": "Fuel price not found"}), 404
    return jsonify({"success": True}), 200
  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    