from scraper import runUserFlights
import pymongo
from dateutil.parser import parse as dateParse
from datetime import datetime, timedelta
import swa.settings as settings

class BookedFlight():
	def __init__(self, origin, date, destination, flightNumber, cost, usingPoints = False):
		self.origin = origin 
		self.date = dateParse(date)
		self.destination = destination
		self.flightNumber = unicode(flightNumber)
		self.cost = cost
		self.usingPoints = usingPoints

	def getFareHistory(self):
		client = pymongo.MongoClient(settings.MONGODB_SERVER, settings.MONGODB_PORT)
		db = client[settings.MONGODB_DB]
		start = self.date
		end = self.date + timedelta(days = 1)
		fares = db['%s_%s' % (self.origin, self.destination)].find({'depart': 
			{'$gte': start, '$lt': end}, 'flight' : {'$elemMatch' : {'$eq' : 
			self.flightNumber}}}).sort('fareValidityDate', pymongo.ASCENDING)
		return fares


if __name__ == '__main__':
	flight1 = BookedFlight('SFO',"02/10/2016",'DEN',3671,104)
	flight2 = BookedFlight('DEN',"03/06/2016",'OAK',1715,6500,True)
	flights = [flight1, flight2]
	#download fares
	runUserFlights(flights)
	#grab prices from DB and compare
	for flight in flights: 
		for fare in flight.getFareHistory():
			print(fare)