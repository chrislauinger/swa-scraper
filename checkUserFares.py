from scraper import runUserFlights
import pymongo
from dateutil.parser import parse as dateParse
from datetime import datetime, timedelta
import swa.settings as settings
from swa.items import *


def fareString(fare):
	return "%s -> %s on %s at %s for $%s or %s points" % (fare['origin'], fare['destination'], 
		fare['depart'].strftime("%m/%d/%Y"), fare['depart'].strftime("%H:%M"), str(fare['price']),
		str(fare['points']))

class BookedFlight():
	def __init__(self, origin, date, destination, flightNumber, cost, usingPoints = False):
		self.origin = origin 
		self.date = dateParse(date)
		self.destination = destination
		self.flightNumber = unicode(flightNumber)
		self.cost = cost
		self.usingPoints = usingPoints
		self.fareHistory = None

	def getFareHistory(self, caching = True):
		if self.fareHistory == None or caching == False:
			client = pymongo.MongoClient(settings.MONGODB_SERVER, settings.MONGODB_PORT)
			db = client[settings.MONGODB_DB]
			start = self.date
			end = self.date + timedelta(days = 1)
			self.fareHistory = db['%s_%s' % (self.origin, self.destination)].find({'depart': 
				{'$gte': start, '$lt': end}, 'flight' : {'$elemMatch' : {'$eq' : 
				self.flightNumber}}}).sort('fareValidityDate', pymongo.DESCENDING)
		return self.fareHistory

	def checkCurrentCost(self):
		#Returns current cost if cheaper, otherwise returns False
		fares = self.getFareHistory()
		mostRecentFare = fares[0]
		fares = self.getFareHistory(False)
		mostRecentFare = fares[0]
		print(fareString(mostRecentFare))
		mostRecentCost = mostRecentFare['points'] if self.usingPoints else mostRecentFare['price']
		if type(mostRecentCost) == str:
			mostRecentCost = int(mostRecentCost.replace(",",""))
		if (mostRecentCost < int(self.cost)):
			print("Found a cheaper fare: %s < %s" % (str(mostRecentCost), self.cost))
			return int(mostRecentCost)
		else:
			print("No savings: %s > %s" % (str(mostRecentCost), self.cost))
			return False


if __name__ == '__main__':
	flights = []
	flights.append(BookedFlight('SFO',"02/10/2016",'DEN',3671,104))
	flights.append(BookedFlight('DEN',"02/15/2016",'OAK',495,9200, True))
	flights.append(BookedFlight('DEN',"02/16/2016",'OAK',495,5800, True))
	flights.append(BookedFlight('SFO',"03/03/2016",'DEN',3671,9200, True))
	flights.append(BookedFlight('DEN',"03/06/2016",'OAK',1715,6500,True))
	#flights.append(BookedFlight('OAK',"04/15/2016",'BZE',1731,11000,True))
	#flights.append(BookedFlight('BZE',"04/15/2016",'OAK',1023,11000,True))
	#download fares
	runUserFlights(flights)
	#grab prices from DB and compare
	for flight in flights: 
		flight.checkCurrentCost()