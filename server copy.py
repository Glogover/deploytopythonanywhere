from flask import Flask, request, jsonify
from fuelStationDAO import fuelStationDAO

app = Flask(__name__, static_url_path="", static_folder="staticpages")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/fuel_stations", methods=["GET"])
def get_all():
    fuel_stations = fuelStationDAO.getAll()
    return jsonify(fuel_stations), 200


@app.route("/fuel_stations/<int:id>", methods=["GET"])
def find_by_id(id):
    fuel_station = fuelStationDAO.findByID(id)
    if not fuel_station:
        return jsonify({"error": "Fuel station not found"}), 404
    return jsonify(fuel_station), 200


@app.route("/fuel_stations", methods=["POST"])
def create():
    data = request.get_json()

    if not data:
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
        "postcode": str(postcode).strip()
    }

    created = fuelStationDAO.create(fuel_station)
    return jsonify(created), 201


@app.route("/fuel_stations/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json()

    if not data:
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

    if "postcode" in data:
        fuel_station["postcode"] = data["postcode"]

    if not fuel_station:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = fuelStationDAO.update(id, fuel_station)
    if not updated:
        return jsonify({"error": "Fuel station not found"}), 404

    return jsonify(updated), 200


@app.route("/fuel_stations/<int:id>", methods=["DELETE"])
def delete(id):
    deleted = fuelStationDAO.delete(id)
    if not deleted:
        return jsonify({"error": "Fuel station not found"}), 404
    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    