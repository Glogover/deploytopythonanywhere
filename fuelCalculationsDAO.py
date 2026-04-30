# fuel calculations DAO - Data Access Object
# This class is responsible for calculation/read-only queries using fuel_prices and fuel_stations tables
# Author: Marcin Kaminski

import mysql.connector
import dbconfig as cfg


class FuelCalculationsDAO:
    def __init__(self):
        self.host = cfg.mysql['host']
        self.user = cfg.mysql['user']
        self.password = cfg.mysql['password']
        self.database = cfg.mysql['database']

    def get_connection(self):
        """Create a new database connection for the current operation.

        Do not store the connection/cursor on self. Flask can handle multiple
        requests at the same time, so shared cursor/connection attributes can be
        overwritten or closed by another request.
        """
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def _fetch_all(self, sql, values=None, converter=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(sql, values or ())
            results = cursor.fetchall()
            if converter is None:
                return results
            return [converter(result) for result in results]
        finally:
            cursor.close()
            connection.close()

    def _fetch_one(self, sql, values=None, converter=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(sql, values or ())
            result = cursor.fetchone()
            if converter is None:
                return result
            return converter(result)
        finally:
            cursor.close()
            connection.close()

    def getLatestPricesByDate(self, price_date):
        sql = """
            SELECT s.name, s.locality, p.petrol_95, p.diesel, p.lpg, p.price_date
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
        """
        values = (price_date,)
        return self._fetch_all(sql, values, self.convertLatestPricesToDictionary)

    def findFuelPricesByLocalityAndDate(self, locality, price_date):
        sql = """
            SELECT s.name, s.locality, p.petrol_95, p.diesel, p.lpg, p.price_date
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE s.locality = %s AND p.price_date = %s
            ORDER BY s.name ASC
        """
        values = (locality, price_date)
        return self._fetch_all(sql, values, self.convertLatestPricesToDictionary)

    def getCheapestPetrol95ByDate(self, price_date):
        sql = """
            SELECT s.name, p.petrol_95
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
            ORDER BY p.petrol_95 ASC
            LIMIT 1
        """
        values = (price_date,)
        return self._fetch_one(sql, values, self.convertCheapestPetrol95ToDictionary)

    def getCheapestDieselByDate(self, price_date):
        sql = """
            SELECT s.name, p.diesel
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
            ORDER BY p.diesel ASC
            LIMIT 1
        """
        values = (price_date,)
        return self._fetch_one(sql, values, self.convertCheapestDieselToDictionary)

    def getCheapestLpgByDate(self, price_date):
        sql = """
            SELECT s.name, p.lpg
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
            ORDER BY p.lpg ASC
            LIMIT 1
        """
        values = (price_date,)
        return self._fetch_one(sql, values, self.convertCheapestLpgToDictionary)

    def getAveragePetrol95ByDay(self):
        sql = """
            SELECT price_date, AVG(petrol_95) AS avg_price
            FROM fuel_prices
            GROUP BY price_date
            ORDER BY price_date DESC
        """
        return self._fetch_all(sql, converter=self.convertAveragePetrol95ToDictionary)

    def getAverageDieselByDay(self):
        sql = """
            SELECT price_date, AVG(diesel) AS avg_price
            FROM fuel_prices
            GROUP BY price_date
            ORDER BY price_date DESC
        """
        return self._fetch_all(sql, converter=self.convertAverageDieselToDictionary)

    def getAverageLpgByDay(self):
        sql = """
            SELECT price_date, AVG(lpg) AS avg_price
            FROM fuel_prices
            GROUP BY price_date
            ORDER BY price_date DESC
        """
        return self._fetch_all(sql, converter=self.convertAverageLpgToDictionary)

    def getAverageAllFuelTypesByDay(self):
        sql = """
            SELECT
                price_date,
                AVG(petrol_95) AS avg_petrol_95,
                AVG(diesel) AS avg_diesel,
                AVG(lpg) AS avg_lpg
            FROM fuel_prices
            GROUP BY price_date
            ORDER BY price_date DESC
        """
        return self._fetch_all(sql, converter=self.convertAverageAllFuelTypesToDictionary)

    def convertLatestPricesToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['name', 'locality', 'petrol_95', 'diesel', 'lpg', 'price_date']
        latest_prices = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            latest_prices[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return latest_prices

    def convertCheapestPetrol95ToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['name', 'petrol_95']
        cheapest_fuel = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            cheapest_fuel[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return cheapest_fuel

    def convertCheapestDieselToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['name', 'diesel']
        cheapest_fuel = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            cheapest_fuel[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return cheapest_fuel

    def convertCheapestLpgToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['name', 'lpg']
        cheapest_fuel = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            cheapest_fuel[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return cheapest_fuel

    def convertAveragePetrol95ToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['price_date', 'avg_petrol_95']
        average_price = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            average_price[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return average_price

    def convertAverageDieselToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['price_date', 'avg_diesel']
        average_price = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            average_price[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return average_price

    def convertAverageLpgToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['price_date', 'avg_lpg']
        average_price = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            average_price[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return average_price

    def convertAverageAllFuelTypesToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['price_date', 'avg_petrol_95', 'avg_diesel', 'avg_lpg']
        average_prices = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            average_prices[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return average_prices


fuelCalculationsDAO = FuelCalculationsDAO()
