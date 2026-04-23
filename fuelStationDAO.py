# fuel station DAO - Data Access Object
# This class is responsible for all interactions with the fuel_stations table in the mySQL database
# Author: Marcin Kaminski


import mysql.connector
import dbconfig as cfg
class FuelStationDAO:
    connection=""
    cursor =''
    host=       ''
    user=       ''
    password=   ''
    database=   ''
    
    def __init__(self):
        self.host=       cfg.mysql['host']
        self.user=       cfg.mysql['user']
        self.password=   cfg.mysql['password']
        self.database=   cfg.mysql['database']

    def getcursor(self): 
        self.connection = mysql.connector.connect(
            host=       self.host,
            user=       self.user,
            password=   self.password,
            database=   self.database,
        )
        self.cursor = self.connection.cursor()
        return self.cursor

    def closeAll(self):
        self.connection.close()
        self.cursor.close()
         
    def getAll(self):
        cursor = self.getcursor()
        sql="select * from fuel_stations"
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []
        #print(results)
        for result in results:
            #print(result)
            returnArray.append(self.convertToDictionary(result))
        
        self.closeAll()
        return returnArray

    def findByID(self, id):
        cursor = self.getcursor()
        sql="select * from fuel_stations where id = %s"
        values = (id,)

        cursor.execute(sql, values)
        result = cursor.fetchone()
        returnvalue = self.convertToDictionary(result)
        self.closeAll()
        return returnvalue

    def create(self, fuel_stations):
        cursor = self.getcursor()
        sql="insert into fuel_stations (name, brand, locality, postcode) values (%s,%s,%s,%s)"
        values = (fuel_stations.get("name"), fuel_stations.get("brand"), fuel_stations.get("locality"), fuel_stations.get("postcode"))
        cursor.execute(sql, values)

        self.connection.commit()
        newid = cursor.lastrowid
        fuel_stations["id"] = newid
        self.closeAll()
        return fuel_stations


    def update(self, id, fuel_stations):
        cursor = self.getcursor()
        sql="update fuel_stations set name= %s,brand=%s, locality=%s, postcode=%s  where id = %s"
        
        values = (fuel_stations.get("name"), fuel_stations.get("brand"), fuel_stations.get("locality"), fuel_stations.get("postcode"),id)
        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()
        
    def delete(self, id):
        cursor = self.getcursor()
        sql="delete from fuel_stations where id = %s"
        values = (id,)

        cursor.execute(sql, values)

        self.connection.commit()
        self.closeAll()
        
        print("delete done")

    def convertToDictionary(self, resultLine):
        attkeys=['id','name','brand', "locality", "postcode"]
        fuel_stations = {}
        currentkey = 0
        for attrib in resultLine:
            fuel_stations[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1 
        return fuel_stations

        
fuelStationDAO = FuelStationDAO()