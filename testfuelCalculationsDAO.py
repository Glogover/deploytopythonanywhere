from decimal import Decimal

from fuelStationDAO import fuelStationDAO
from fuelPricesDAO import fuelPricesDAO
from fuelCalculationsDAO import fuelCalculationsDAO


# Test data
price_date = "2026-04-17"
locality = "Dublin"

fuel_station_1 = {
    "name": "Test Station One",
    "brand": "Test Brand",
    "locality": locality,
    "postcode": "D01 1111",
}

fuel_station_2 = {
    "name": "Test Station Two",
    "brand": "Test Brand",
    "locality": locality,
    "postcode": "D02 2222",
}

# create fuel stations
fuel_station_1 = fuelStationDAO.create(fuel_station_1)
fuel_station_2 = fuelStationDAO.create(fuel_station_2)

fuel_station_1_id = fuel_station_1["id"]
fuel_station_2_id = fuel_station_2["id"]

fuel_price_1 = {
    "station_id": fuel_station_1_id,
    "petrol_95": Decimal("1.50"),
    "diesel": Decimal("1.70"),
    "lpg": Decimal("0.80"),
    "price_date": price_date,
}

fuel_price_2 = {
    "station_id": fuel_station_2_id,
    "petrol_95": Decimal("1.40"),
    "diesel": Decimal("1.60"),
    "lpg": Decimal("0.75"),
    "price_date": price_date,
}

# create fuel prices
fuel_price_1 = fuelPricesDAO.create(fuel_price_1)
fuel_price_2 = fuelPricesDAO.create(fuel_price_2)

fuel_price_1_id = fuel_price_1["id"]
fuel_price_2_id = fuel_price_2["id"]

# get latest prices by date
print("test get latest prices by date")
latest_prices = fuelCalculationsDAO.getLatestPricesByDate(price_date)
print(latest_prices)
assert isinstance(latest_prices, list)
assert len(latest_prices) > 0

# find fuel prices by locality and date
print("test find fuel prices by locality and date")
prices_by_locality = fuelCalculationsDAO.findFuelPricesByLocalityAndDate(locality, price_date)
print(prices_by_locality)
assert isinstance(prices_by_locality, list)
assert len(prices_by_locality) >= 2
for price in prices_by_locality:
    assert price["locality"] == locality
    assert str(price["price_date"]) == price_date

# cheapest petrol_95 by date
print("test cheapest petrol_95 by date")
cheapest_petrol_95 = fuelCalculationsDAO.getCheapestPetrol95ByDate(price_date)
print(cheapest_petrol_95)
assert cheapest_petrol_95 is not None
assert cheapest_petrol_95["petrol_95"] == Decimal("1.40")

# cheapest diesel by date
print("test cheapest diesel by date")
cheapest_diesel = fuelCalculationsDAO.getCheapestDieselByDate(price_date)
print(cheapest_diesel)
assert cheapest_diesel is not None
assert cheapest_diesel["diesel"] == Decimal("1.60")

# cheapest lpg by date
print("test cheapest lpg by date")
cheapest_lpg = fuelCalculationsDAO.getCheapestLpgByDate(price_date)
print(cheapest_lpg)
assert cheapest_lpg is not None
assert cheapest_lpg["lpg"] == Decimal("0.75")

# average petrol_95 by day
print("test average petrol_95 by day")
average_petrol_95 = fuelCalculationsDAO.getAveragePetrol95ByDay()
print(average_petrol_95)
assert isinstance(average_petrol_95, list)
assert len(average_petrol_95) > 0

# average diesel by day
print("test average diesel by day")
average_diesel = fuelCalculationsDAO.getAverageDieselByDay()
print(average_diesel)
assert isinstance(average_diesel, list)
assert len(average_diesel) > 0

# average lpg by day
print("test average lpg by day")
average_lpg = fuelCalculationsDAO.getAverageLpgByDay()
print(average_lpg)
assert isinstance(average_lpg, list)
assert len(average_lpg) > 0

# average all fuel types by day
print("test average all fuel types by day")
average_all_fuel_types = fuelCalculationsDAO.getAverageAllFuelTypesByDay()
print(average_all_fuel_types)
assert isinstance(average_all_fuel_types, list)
assert len(average_all_fuel_types) > 0

# delete test data
# Uncomment these lines if you want to remove test records after running the test.
# fuelPricesDAO.delete(fuel_price_1_id)
# fuelPricesDAO.delete(fuel_price_2_id)
# fuelStationDAO.delete(fuel_station_1_id)
# fuelStationDAO.delete(fuel_station_2_id)
