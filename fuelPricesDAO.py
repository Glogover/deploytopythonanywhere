# fuel prices DAO - Data Access Object
# This class is responsible for all interactions with the fuel_prices table in the mySQL database
# Author: Marcin Kaminski

import mysql.connector
import dbconfig as cfg


class FuelPricesDAO:
    connection = None
    cursor = None
    host = ''
    user = ''
    password = ''
    database = ''

    def __init__(self):
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

    def getAll(self):
        cursor = self.getcursor()
        sql = "select * from fuel_prices"
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []

        for result in results:
            returnArray.append(self.convertToDictionary(result))

        self.closeAll()
        return returnArray

    def findByID(self, id):
        cursor = self.getcursor()
        sql = "select * from fuel_prices where id = %s"
        values = (id,)

        cursor.execute(sql, values)
        result = cursor.fetchone()
        returnvalue = self.convertToDictionary(result)
        self.closeAll()
        return returnvalue

    def create(self, fuel_prices):
        cursor = self.getcursor()
        sql = "insert into fuel_prices (station_id, petrol_95, diesel, lpg, price_date) values (%s,%s,%s,%s,%s)"
        values = (
            fuel_prices.get("station_id"),
            fuel_prices.get("petrol_95"),
            fuel_prices.get("diesel"),
            fuel_prices.get("lpg"),
            fuel_prices.get("price_date"),
        )
        cursor.execute(sql, values)

        self.connection.commit()
        newid = cursor.lastrowid
        fuel_prices["id"] = newid
        self.closeAll()
        return fuel_prices

    def update(self, id, fuel_prices):
        cursor = self.getcursor()
        sql = "update fuel_prices set station_id=%s, petrol_95=%s, diesel=%s, lpg=%s, price_date=%s where id = %s"

        values = (
            fuel_prices.get("station_id"),
            fuel_prices.get("petrol_95"),
            fuel_prices.get("diesel"),
            fuel_prices.get("lpg"),
            fuel_prices.get("price_date"),
            id,
        )
        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()

    def delete(self, id):
        cursor = self.getcursor()
        sql = "delete from fuel_prices where id = %s"
        values = (id,)

        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()

        print("delete done")

    def convertToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['id', 'station_id', 'petrol_95', 'diesel', 'lpg', 'price_date']
        fuel_prices = {}
        currentkey = 0
        for attrib in resultLine:
            fuel_prices[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return fuel_prices


fuelPricesDAO = FuelPricesDAO()
