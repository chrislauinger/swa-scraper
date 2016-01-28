from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta
import pymongo
import time
import boto3

TABLE_NAME = 'fares'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'


#script to move fare data from mongo db to dynamo db

def toMsEpoch(date):
	tt = datetime.timetuple(date)
	sec_epoch_loc = int(time.mktime(tt) * 1000)
	return sec_epoch_loc

def fromMsEpoch(ms):
	s = ms / 1000.0
	date = datetime.fromtimestamp(s)
	return date

class Fare():
	def __init__(self, mongoDict):
		self.origin = mongoDict['origin']
		self.destination = mongoDict['destination']
		self.connectingArpts = mongoDict['connectingArpts']
		self.flight = mongoDict['flight']
		self.arrive = toMsEpoch(mongoDict['arrive'])
		self.depart = toMsEpoch(mongoDict['depart'])
		self.faretype = mongoDict['faretype']
		self.price = int(mongoDict['price'])
		self.fareValidityDate = toMsEpoch(mongoDict['fareValidityDate'])
		self.points = str(mongoDict['points'])
		self.points = int(self.points.replace(",",""))
		self.stops = mongoDict['stops']

	def getDynamoDbItem(self):
		return {
			'route' : self.origin + "_" + self.destination,
			'sort_key' : str(self.depart) + "_" + str(self.fareValidityDate),
        	'origin': self.origin,
        	'destination': self.destination,
        	'connecting_arpts': self.connectingArpts,
        	'flight' : self.flight,
        	'arrive' : self.arrive,
        	'depart' : self.depart,
        	'faretype' : self.faretype,
        	'price' : self.price,	
        	'fare_validity_date' : self.fareValidityDate,
        	'points' : self.points,
        	'stops' : self.stops
    	}


def getFaresFromMongo(routeString,db):
	fares = db[routeString].find()
	return fares


def putFaresInDynamo(table,fare):
	table.put_item(Item= fare.getDynamoDbItem())

if __name__ == '__main__':
	
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	client = pymongo.MongoClient(settings.MONGODB_SERVER, settings.MONGODB_PORT)
	db = client[settings.MONGODB_DB]
	limit = 1000
	for pair in getCityPairs():
		if (pair[0] == 'SEA' and pair[1] == 'BWI'): 
			continue;
		a = time.time()
		print(pair)
		routeString = pair[0] + "_" + pair[1]
		fares = getFaresFromMongo(routeString,db)
		fares.batch_size(50)
		i = 0;
		for fare in fares:
			if i > limit: 
				break
			i = i + 1
			if (i % 100 == 0):
				print("running")
			putFaresInDynamo(table,Fare(fare))
		print("put time: " + str(time.time() - a) + " for " + str(i))
		fares.close()

	
	