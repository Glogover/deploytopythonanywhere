# fuel station DAO - Data Access Object
# This class is responsible for all interactions with the fuel_stations table in the MySQL database
# Author: Marcin Kaminski

import mysql.connector
import dbconfig as cfg


class FuelStationDAO:
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

    def getAll(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = "select * from fuel_stations"
            cursor.execute(sql)
            results = cursor.fetchall()
            return [self.convertToDictionary(result) for result in results]
        finally:
            cursor.close()
            connection.close()

    def findByID(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = "select * from fuel_stations where id = %s"
            values = (id,)
            cursor.execute(sql, values)
            result = cursor.fetchone()
            return self.convertToDictionary(result) if result is not None else None
        finally:
            cursor.close()
            connection.close()

    def create(self, fuel_station):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = "insert into fuel_stations (name, brand, locality, postcode) values (%s,%s,%s,%s)"
            values = (
                fuel_station.get("name"),
                fuel_station.get("brand"),
                fuel_station.get("locality"),
                fuel_station.get("postcode"),
            )
            cursor.execute(sql, values)
            connection.commit()

            newid = cursor.lastrowid
            fuel_station["id"] = newid
            return fuel_station
        finally:
            cursor.close()
            connection.close()

    def update(self, id, fuel_station):
        """Update only the supplied fields and return the updated row, or None."""
        allowed_fields = ["name", "brand", "locality", "postcode"]
        fields_to_update = [field for field in allowed_fields if field in fuel_station]

        if not fields_to_update:
            return None

        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            set_clause = ", ".join([f"{field}=%s" for field in fields_to_update])
            sql = f"update fuel_stations set {set_clause} where id = %s"
            values = tuple(fuel_station.get(field) for field in fields_to_update) + (id,)

            cursor.execute(sql, values)
            connection.commit()

            if cursor.rowcount == 0:
                return None

            return self.findByID(id)
        finally:
            cursor.close()
            connection.close()

    def delete(self, id):
        """Delete a fuel station and return True if a row was deleted."""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = "delete from fuel_stations where id = %s"
            values = (id,)
            cursor.execute(sql, values)
            connection.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            connection.close()

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
