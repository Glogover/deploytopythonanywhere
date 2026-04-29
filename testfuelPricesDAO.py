from decimal import Decimal

from fuelStationDAO import fuelStationDAO
from fuelPricesDAO import fuelPricesDAO


fuel_station = {
    "name": "Test Station For Fuel Prices DAO",
    "brand": "Test Brand",
    "locality": "Dublin",
    "postcode": "D01 9999",
}

fuel_station_id = None
fuel_price_id = None

try:
    # create a real station instead of assuming station_id 1 exists
    created_station = fuelStationDAO.create(fuel_station.copy())
    fuel_station_id = created_station["id"]

    fuel_price = {
        "station_id": fuel_station_id,
        "petrol_95": Decimal("1.50"),
        "diesel": Decimal("2.00"),
        "lpg": Decimal("0.80"),
        "price_date": "2026-04-01",
    }

    # create
    created_price = fuelPricesDAO.create(fuel_price.copy())
    fuel_price_id = created_price["id"]

    # find by id
    print("test create and find by id")
    result = fuelPricesDAO.findByID(fuel_price_id)
    print(result)
    assert result is not None
    assert result["id"] == fuel_price_id
    assert result["station_id"] == fuel_station_id
    assert result["petrol_95"] == fuel_price["petrol_95"]
    assert result["diesel"] == fuel_price["diesel"]
    assert result["lpg"] == fuel_price["lpg"]
    assert str(result["price_date"]) == fuel_price["price_date"]

    # update all fields
    print("test update")
    new_fuel_price = {
        "station_id": fuel_station_id,
        "petrol_95": Decimal("1.60"),
        "diesel": Decimal("2.10"),
        "lpg": Decimal("0.85"),
        "price_date": "2026-04-02",
    }
    updated_price = fuelPricesDAO.update(fuel_price_id, new_fuel_price)
    print(updated_price)
    assert updated_price is not None
    assert updated_price["id"] == fuel_price_id
    assert updated_price["station_id"] == fuel_station_id
    assert updated_price["petrol_95"] == new_fuel_price["petrol_95"]
    assert updated_price["diesel"] == new_fuel_price["diesel"]
    assert updated_price["lpg"] == new_fuel_price["lpg"]
    assert str(updated_price["price_date"]) == new_fuel_price["price_date"]

    # partial update
    print("test partial update")
    partially_updated_price = fuelPricesDAO.update(fuel_price_id, {"diesel": Decimal("2.20")})
    print(partially_updated_price)
    assert partially_updated_price is not None
    assert partially_updated_price["diesel"] == Decimal("2.20")
    assert partially_updated_price["petrol_95"] == new_fuel_price["petrol_95"]

    # empty update should return None
    print("test empty update")
    assert fuelPricesDAO.update(fuel_price_id, {}) is None

    # get all
    print("test get all")
    all_fuel_prices = fuelPricesDAO.getAll()
    assert isinstance(all_fuel_prices, list)
    assert any(price["id"] == fuel_price_id for price in all_fuel_prices)

    # missing id
    print("test missing id")
    assert fuelPricesDAO.findByID(-1) is None
    assert fuelPricesDAO.update(-1, {"diesel": Decimal("2.30")}) is None
    assert fuelPricesDAO.delete(-1) is False

finally:
    # delete child row before parent station row
    if fuel_price_id is not None:
        fuelPricesDAO.delete(fuel_price_id)
        assert fuelPricesDAO.findByID(fuel_price_id) is None
    if fuel_station_id is not None:
        fuelStationDAO.delete(fuel_station_id)
