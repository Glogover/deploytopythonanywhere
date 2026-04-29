from fuelStationDAO import fuelStationDAO


fuel_station = {
    "name": "Test Station DAO",
    "brand": "Test Brand",
    "locality": "Dublin",
    "postcode": "D01 1234",
}

fuel_station_id = None

try:
    # create
    created_station = fuelStationDAO.create(fuel_station.copy())
    fuel_station_id = created_station["id"]

    # find by id
    print("test create and find by id")
    result = fuelStationDAO.findByID(fuel_station_id)
    print(result)
    assert result is not None
    assert result["id"] == fuel_station_id
    assert result["name"] == fuel_station["name"]
    assert result["brand"] == fuel_station["brand"]
    assert result["locality"] == fuel_station["locality"]
    assert result["postcode"] == fuel_station["postcode"]

    # update all fields
    print("test update")
    new_fuel_station = {
        "name": "Updated Test Station DAO",
        "brand": "Updated Test Brand",
        "locality": "Cork",
        "postcode": "C01 5678",
    }
    updated_station = fuelStationDAO.update(fuel_station_id, new_fuel_station)
    print(updated_station)
    assert updated_station is not None
    assert updated_station["id"] == fuel_station_id
    assert updated_station["name"] == new_fuel_station["name"]
    assert updated_station["brand"] == new_fuel_station["brand"]
    assert updated_station["locality"] == new_fuel_station["locality"]
    assert updated_station["postcode"] == new_fuel_station["postcode"]

    # partial update
    print("test partial update")
    partially_updated_station = fuelStationDAO.update(fuel_station_id, {"locality": "Galway"})
    print(partially_updated_station)
    assert partially_updated_station is not None
    assert partially_updated_station["locality"] == "Galway"
    assert partially_updated_station["postcode"] == new_fuel_station["postcode"]

    # empty update should return None
    print("test empty update")
    assert fuelStationDAO.update(fuel_station_id, {}) is None

    # get all
    print("test get all")
    all_fuel_stations = fuelStationDAO.getAll()
    assert isinstance(all_fuel_stations, list)
    assert any(station["id"] == fuel_station_id for station in all_fuel_stations)

    # missing id
    print("test missing id")
    assert fuelStationDAO.findByID(-1) is None
    assert fuelStationDAO.update(-1, {"locality": "Nowhere"}) is None
    assert fuelStationDAO.delete(-1) is False

finally:
    # delete test data
    if fuel_station_id is not None:
        fuelStationDAO.delete(fuel_station_id)
        assert fuelStationDAO.findByID(fuel_station_id) is None
