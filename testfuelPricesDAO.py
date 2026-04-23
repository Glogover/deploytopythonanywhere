from decimal import Decimal

from fuelPricesDAO import fuelPricesDAO


fuel_price = {
    "station_id": Decimal("1"),
    "petrol_95": Decimal("1.50"),
    "diesel": Decimal("2.00"),
    "lpg": Decimal("0.80"),
    "price_date": "2026-04-01",
}

# create
fuel_price = fuelPricesDAO.create(fuel_price)
fuel_priceid = fuel_price["id"]

# find by id
result = fuelPricesDAO.findByID(fuel_priceid)
print("test create and find by id")
print(result)
assert result is not None
assert result["id"] == fuel_priceid
assert result["station_id"] == fuel_price["station_id"]

# update
new_fuel_price = {
    "station_id": Decimal("1"),
    "petrol_95": Decimal("1.60"),
    "diesel": Decimal("2.10"),
    "lpg": Decimal("0.85"),
    "price_date": "2026-04-01",
}
fuelPricesDAO.update(fuel_priceid, new_fuel_price)
result = fuelPricesDAO.findByID(fuel_priceid)
print("test update")
print(result)
assert result["petrol_95"] == new_fuel_price["petrol_95"]
assert result["diesel"] == new_fuel_price["diesel"]
assert result["lpg"] == new_fuel_price["lpg"]

# get all
print("test get all")
allFuelPrices = fuelPricesDAO.getAll()
assert isinstance(allFuelPrices, list)
for fuel_price in allFuelPrices:
    print(fuel_price)

# delete
# fuelPricesDAO.delete(fuel_priceid)
