from fuelPricesDAO import fuelPricesDAO


fuel_price = {
  "station_id":1, 
  "petrol_95":1.50,
  "diesel":2.00,
  "lpg":0.80,
  "price_date":"2026-04-01"
  }
#create
fuel_price = fuelPricesDAO.create(fuel_price)
fuel_priceid = fuel_price["id"]
# find by id
result = fuelPricesDAO.findByID(fuel_priceid)
print ("test create and find by id")
print (result)

#update
new_fuel_price= {"station_id":1, "petrol_95":1.60, "diesel":2.10, "lpg":0.85, "price_date":"2026-04-01"}
fuelPricesDAO.update(fuel_priceid,new_fuel_price)
result = fuelPricesDAO.findByID(fuel_priceid)
print("test update")
print (result)

# get all 
print("test get all")
allFuelPrices = fuelPricesDAO.getAll()
for fuel_price in allFuelPrices:
  print(fuel_price)

# delete
#fuelPricesDAO.delete(fuel_priceid)

