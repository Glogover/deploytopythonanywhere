# fuel station DAO - Data Access Object
# This class is responsible for all interactions with the fuel_stations table in the mySQL database
# Author: Marcin Kaminski

import mysql.connector
import dbconfig as cfg


class FuelStationDAO:
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

    def getAll(self):
        cursor = self.getcursor()
        sql = "select * from fuel_stations"
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []
        for result in results:
            returnArray.append(self.convertToDictionary(result))

        self.closeAll()
        return returnArray

    def findByID(self, id):
        cursor = self.getcursor()
        sql = "select * from fuel_stations where id = %s"
        values = (id,)

        cursor.execute(sql, values)
        result = cursor.fetchone()
        returnvalue = self.convertToDictionary(result) if result is not None else None
        self.closeAll()
        return returnvalue

    def create(self, fuel_station):
        cursor = self.getcursor()
        sql = "insert into fuel_stations (name, brand, locality, postcode) values (%s,%s,%s,%s)"
        values = (
            fuel_station.get("name"),
            fuel_station.get("brand"),
            fuel_station.get("locality"),
            fuel_station.get("postcode"),
        )
        cursor.execute(sql, values)

        self.connection.commit()
        newid = cursor.lastrowid
        fuel_station["id"] = newid
        self.closeAll()
        return fuel_station

    def update(self, id, fuel_station):
        cursor = self.getcursor()
        sql = "update fuel_stations set name=%s, brand=%s, locality=%s, postcode=%s where id = %s"

        values = (
            fuel_station.get("name"),
            fuel_station.get("brand"),
            fuel_station.get("locality"),
            fuel_station.get("postcode"),
            id,
        )
        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()

    def delete(self, id):
        cursor = self.getcursor()
        sql = "delete from fuel_stations where id = %s"
        values = (id,)

        cursor.execute(sql, values)

        self.connection.commit()
        self.closeAll()
        print("delete done")

    def convertToDictionary(self, resultLine):
        if resultLine is None:
            return None

        attkeys = ['id', 'name', 'brand', 'locality', 'postcode']
        fuel_station = {}
        currentkey = 0
        for attrib in resultLine:
            if currentkey >= len(attkeys):
                break
            fuel_station[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return fuel_station


fuelStationDAO = FuelStationDAO()
