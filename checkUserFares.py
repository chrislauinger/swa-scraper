from scraper import runUserFlights
import pymongo
from dateutil.parser import parse as dateParse
from datetime import datetime, timedelta
import swa.settings as settings
from datetime import datetime, timedelta

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
		print(mostRecentFare)
		if (mostRecentFare['fareValidityDate'] < (datetime.now() - timedelta(days = 1))):
			runUserFlights([self])
		fares = self.getFareHistory(False)
		mostRecentFare = fares[0]
		mostRecentCost = mostRecentFare['points'] if self.usingPoints else mostRecentFare['price']
		if (int(mostRecentCost.replace(",","")) < int(self.cost)):
			print("Found a cheaper fare: " + str(mostRecentCost))
			return int(mostRecentCost)
		else:
			return False


if __name__ == '__main__':
	flight1 = BookedFlight('SFO',"02/10/2016",'DEN',3671,104)
	flight2 = BookedFlight('DEN',"03/06/2016",'OAK',1715,6500,True)
	flights = [flight1, flight2]
	#download fares
	#runUserFlights(flights)
	#grab prices from DB and compare
	for flight in flights: 
		flight.checkCurrentCost()