from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta
from userFlights_db import *
from user_db import *

#dynamo db for fares
TABLE_NAME = 'fares'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'

class Fare():
	def __init__(self, item):
		self.origin = item['origin'] 
		self.destination = item['destination'] 
		self.route = item['route'] 
		self.sort_key = item['sort_key']
		self.connecting_arpts = item['connecting_arpts']
		self.depart = fromMsEpoch(int(item['depart']))
		self.arrive = fromMsEpoch(int(item['arrive']))
		self.fare_validity_date = fromMsEpoch(int(item['fare_validity_date']))
		self.flight = item['flight']
		self.flight_key = item['flight_key']
		self.points = item['points']
		self.price = item['price']
		self.stops = item['stops']

	def __str__(self):
		return "%s points or $%s at %s" % (self.points, self.price, self.fare_validity_date) 


def dynamoResponseToObjects(response):
	fares = []
	for item in response['Items']:
		fares.append(Fare(item))
	return fares

def getFaresForFlight(userFlight):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.query(KeyConditionExpression=Key('route').eq(userFlight.route),
		FilterExpression=Key('flight_key').eq(userFlight.flightKey))
	return dynamoResponseToObjects(response)


def checkForRefunds():
	flights = getAllFlights()
	for flight in flights:
		print(flight)
		fares = getFaresForFlight(flight)
		flight.addFares(fares)
		refund = flight.checkRefund() 
		if refund:
			sendEmail(getUser(flight.username).email, 'Southwest Refund Found: ' + flight.basicStr(), refund)
			#email
			print(refund)


if __name__ == '__main__':
	checkForRefunds()
	