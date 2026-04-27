# fuel calculations DAO - Data Access Object
# This class is responsible for calculation/read-only queries using fuel_prices and fuel_stations tables
# Author: Marcin Kaminski

import mysql.connector
import dbconfig as cfg


class FuelCalculationsDAO:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.host = cfg.mysql['host']
        self.user = cfg.mysql['user']
        self.password = cfg.mysql['password']
        self.database = cfg.mysql['database']

    def getcursor(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self.cursor = self.connection.cursor()
        return self.cursor

    def closeAll(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def getLatestPricesByDate(self, price_date):
        cursor = self.getcursor()
        sql = """
            SELECT s.name, s.locality, p.petrol_95, p.diesel, p.lpg, p.price_date
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
        """
        values = (price_date,)
        cursor.execute(sql, values)
        results = cursor.fetchall()

        returnArray = []
        for result in results:
            returnArray.append(self.convertLatestPricesToDictionary(result))

        self.closeAll()
        return returnArray

    def findFuelPricesByLocalityAndDate(self, locality, price_date):
        cursor = self.getcursor()
        sql = """
            SELECT s.name, s.locality, p.petrol_95, p.diesel, p.lpg, p.price_date
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE s.locality = %s AND p.price_date = %s
            ORDER BY s.name ASC
        """
        values = (locality, price_date)
        cursor.execute(sql, values)
        results = cursor.fetchall()

        returnArray = []
        for result in results:
            returnArray.append(self.convertLatestPricesToDictionary(result))

        self.closeAll()
        return returnArray

    def getCheapestPetrol95ByDate(self, price_date):
        cursor = self.getcursor()
        sql = """
            SELECT s.name, p.petrol_95
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
            ORDER BY p.petrol_95 ASC
            LIMIT 1
        """
        values = (price_date,)
        cursor.execute(sql, values)
        result = cursor.fetchone()

        returnvalue = self.convertCheapestPetrol95ToDictionary(result)
        self.closeAll()
        return returnvalue

    def getCheapestDieselByDate(self, price_date):
        cursor = self.getcursor()
        sql = """
            SELECT s.name, p.diesel
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
            ORDER BY p.diesel ASC
            LIMIT 1
        """
        values = (price_date,)
        cursor.execute(sql, values)
        result = cursor.fetchone()

        returnvalue = self.convertCheapestDieselToDictionary(result)
        self.closeAll()
        return returnvalue

    def getCheapestLpgByDate(self, price_date):
        cursor = self.getcursor()
        sql = """
            SELECT s.name, p.lpg
            FROM fuel_prices p
            JOIN fuel_stations s ON p.station_id = s.id
            WHERE p.price_date = %s
            ORDER BY p.lpg ASC
            LIMIT 1
        """
        values = (price_date,)
        cursor.execute(sql, values)
        result = cursor.fetchone()

        returnvalue = self.convertCheapestLpgToDictionary(result)
        self.closeAll()
        return returnvalue

    def getAveragePetrol95ByDay(self):
        cursor = self.getcursor()
        sql = """
            SELECT price_date, AVG(petrol_95) AS avg_price
            FROM fuel_prices
            GROUP BY price_date
        """
        cursor.execute(sql)
        results = cursor.fetchall()

        returnArray = []
        for result in results:
            returnArray.append(self.convertAveragePetrol95ToDictionary(result))

        self.closeAll()
        return returnArray

    def getAverageDieselByDay(self):
        cursor = self.getcursor()
        sql = """
            SELECT price_date, AVG(diesel) AS avg_price
            FROM fuel_prices
            GROUP BY price_date
        """
        cursor.execute(sql)
        results = cursor.fetchall()

        returnArray = []
        for result in results:
            returnArray.append(self.convertAverageDieselToDictionary(result))

        self.closeAll()
        return returnArray

    def getAverageLpgByDay(self):
        cursor = self.getcursor()
        sql = """
            SELECT price_date, AVG(lpg) AS avg_price
            FROM fuel_prices
            GROUP BY price_date
        """
        cursor.execute(sql)
        results = cursor.fetchall()

        returnArray = []
        for result in results:
            returnArray.append(self.convertAverageLpgToDictionary(result))

        self.closeAll()
        return returnArray

    def getAverageAllFuelTypesByDay(self):
        cursor = self.getcursor()
        sql = """
            SELECT
                price_date,
                AVG(petrol_95) AS avg_petrol_95,
                AVG(diesel) AS avg_diesel,
                AVG(lpg) AS avg_lpg
            FROM fuel_prices
            GROUP BY price_date
        """
        cursor.execute(sql)
        results = cursor.fetchall()

        returnArray = []
        for result in results:
            returnArray.append(self.convertAverageAllFuelTypesToDictionary(result))

        self.closeAll()
        return returnArray

    def convertLatestPricesToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['name', 'locality', 'petrol_95', 'diesel', 'lpg', 'price_date']
        latest_prices = {}
        currentkey = 0
        for attrib in resultLine:
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
            average_prices[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return average_prices


fuelCalculationsDAO = FuelCalculationsDAO()
