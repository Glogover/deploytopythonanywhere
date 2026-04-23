from fuelStationDAO import fuelStationDAO


fuel_station = {
    "name": "Marvin",
    "brand": "Marvin",
    "locality": "Dublin",
    "postcode": "D01 1234",
}

# create
fuel_station = fuelStationDAO.create(fuel_station)
fuel_stationid = fuel_station["id"]

# find by id
result = fuelStationDAO.findByID(fuel_stationid)
print("test create and find by id")
print(result)
assert result is not None
assert result["id"] == fuel_stationid

# update
new_fuel_station = {
    "name": "Marvin",
    "brand": "Marvin",
    "locality": "Cork",
    "postcode": "C01 5678",
}
fuelStationDAO.update(fuel_stationid, new_fuel_station)
result = fuelStationDAO.findByID(fuel_stationid)
print("test update")
print(result)
assert result is not None
assert result["locality"] == "Cork"
assert result["postcode"] == "C01 5678"

# get all
print("test get all")
allFuelStations = fuelStationDAO.getAll()
assert isinstance(allFuelStations, list)
for fuel_station in allFuelStations:
    print(fuel_station)

# delete
# fuelStationDAO.delete(fuel_stationid)
