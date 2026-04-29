from decimal import Decimal

from fuelStationDAO import fuelStationDAO
from fuelPricesDAO import fuelPricesDAO
from fuelCalculationsDAO import fuelCalculationsDAO


# Test data
price_date = "2099-04-17"
missing_price_date = "2099-04-18"
locality = "DAO Calculation Test Locality"

fuel_station_1 = {
    "name": "DAO Calculation Test Station One",
    "brand": "Test Brand",
    "locality": locality,
    "postcode": "D01 1111",
}

fuel_station_2 = {
    "name": "DAO Calculation Test Station Two",
    "brand": "Test Brand",
    "locality": locality,
    "postcode": "D02 2222",
}

fuel_station_1_id = None
fuel_station_2_id = None
fuel_price_1_id = None
fuel_price_2_id = None

try:
    # create fuel stations
    fuel_station_1 = fuelStationDAO.create(fuel_station_1.copy())
    fuel_station_2 = fuelStationDAO.create(fuel_station_2.copy())

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
    fuel_price_1 = fuelPricesDAO.create(fuel_price_1.copy())
    fuel_price_2 = fuelPricesDAO.create(fuel_price_2.copy())

    fuel_price_1_id = fuel_price_1["id"]
    fuel_price_2_id = fuel_price_2["id"]

    # get latest prices by date
    print("test get latest prices by date")
    latest_prices = fuelCalculationsDAO.getLatestPricesByDate(price_date)
    print(latest_prices)
    assert isinstance(latest_prices, list)
    assert len(latest_prices) >= 2
    test_station_names = {"DAO Calculation Test Station One", "DAO Calculation Test Station Two"}
    test_latest_prices = [price for price in latest_prices if price["name"] in test_station_names]
    assert len(test_latest_prices) == 2
    for price in test_latest_prices:
        assert price["locality"] == locality
        assert str(price["price_date"]) == price_date
        assert set(price.keys()) == {"name", "locality", "petrol_95", "diesel", "lpg", "price_date"}

    # find fuel prices by locality and date
    print("test find fuel prices by locality and date")
    prices_by_locality = fuelCalculationsDAO.findFuelPricesByLocalityAndDate(locality, price_date)
    print(prices_by_locality)
    assert isinstance(prices_by_locality, list)
    assert len(prices_by_locality) == 2
    assert [price["name"] for price in prices_by_locality] == sorted([price["name"] for price in prices_by_locality])
    for price in prices_by_locality:
        assert price["locality"] == locality
        assert str(price["price_date"]) == price_date

    # cheapest petrol_95 by date
    print("test cheapest petrol_95 by date")
    cheapest_petrol_95 = fuelCalculationsDAO.getCheapestPetrol95ByDate(price_date)
    print(cheapest_petrol_95)
    assert cheapest_petrol_95 is not None
    assert cheapest_petrol_95["name"] == "DAO Calculation Test Station Two"
    assert cheapest_petrol_95["petrol_95"] == Decimal("1.40")

    # cheapest diesel by date
    print("test cheapest diesel by date")
    cheapest_diesel = fuelCalculationsDAO.getCheapestDieselByDate(price_date)
    print(cheapest_diesel)
    assert cheapest_diesel is not None
    assert cheapest_diesel["name"] == "DAO Calculation Test Station Two"
    assert cheapest_diesel["diesel"] == Decimal("1.60")

    # cheapest lpg by date
    print("test cheapest lpg by date")
    cheapest_lpg = fuelCalculationsDAO.getCheapestLpgByDate(price_date)
    print(cheapest_lpg)
    assert cheapest_lpg is not None
    assert cheapest_lpg["name"] == "DAO Calculation Test Station Two"
    assert cheapest_lpg["lpg"] == Decimal("0.75")

    # missing date should return empty list / None
    print("test missing date")
    assert fuelCalculationsDAO.getLatestPricesByDate(missing_price_date) == []
    assert fuelCalculationsDAO.findFuelPricesByLocalityAndDate(locality, missing_price_date) == []
    assert fuelCalculationsDAO.getCheapestPetrol95ByDate(missing_price_date) is None
    assert fuelCalculationsDAO.getCheapestDieselByDate(missing_price_date) is None
    assert fuelCalculationsDAO.getCheapestLpgByDate(missing_price_date) is None

    # average petrol_95 by day
    print("test average petrol_95 by day")
    average_petrol_95 = fuelCalculationsDAO.getAveragePetrol95ByDay()
    print(average_petrol_95)
    assert isinstance(average_petrol_95, list)
    petrol_average_for_test_date = next(row for row in average_petrol_95 if str(row["price_date"]) == price_date)
    assert petrol_average_for_test_date["avg_petrol_95"] == Decimal("1.450000")

    # average diesel by day
    print("test average diesel by day")
    average_diesel = fuelCalculationsDAO.getAverageDieselByDay()
    print(average_diesel)
    assert isinstance(average_diesel, list)
    diesel_average_for_test_date = next(row for row in average_diesel if str(row["price_date"]) == price_date)
    assert diesel_average_for_test_date["avg_diesel"] == Decimal("1.650000")

    # average lpg by day
    print("test average lpg by day")
    average_lpg = fuelCalculationsDAO.getAverageLpgByDay()
    print(average_lpg)
    assert isinstance(average_lpg, list)
    lpg_average_for_test_date = next(row for row in average_lpg if str(row["price_date"]) == price_date)
    assert lpg_average_for_test_date["avg_lpg"] == Decimal("0.775000")

    # average all fuel types by day
    print("test average all fuel types by day")
    average_all_fuel_types = fuelCalculationsDAO.getAverageAllFuelTypesByDay()
    print(average_all_fuel_types)
    assert isinstance(average_all_fuel_types, list)
    averages_for_test_date = next(row for row in average_all_fuel_types if str(row["price_date"]) == price_date)
    assert averages_for_test_date["avg_petrol_95"] == Decimal("1.450000")
    assert averages_for_test_date["avg_diesel"] == Decimal("1.650000")
    assert averages_for_test_date["avg_lpg"] == Decimal("0.775000")

finally:
    # delete test data. Child rows must be deleted before parent station rows.
    if fuel_price_1_id is not None:
        fuelPricesDAO.delete(fuel_price_1_id)
    if fuel_price_2_id is not None:
        fuelPricesDAO.delete(fuel_price_2_id)
    if fuel_station_1_id is not None:
        fuelStationDAO.delete(fuel_station_1_id)
    if fuel_station_2_id is not None:
        fuelStationDAO.delete(fuel_station_2_id)
