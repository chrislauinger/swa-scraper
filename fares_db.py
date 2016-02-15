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


	def detailedString(self):
		return self.sort_key

def dynamoResponseToObjects(response):
	fares = []
	for item in response['Items']:
		fares.append(Fare(item))
	
	return fares

def getFaresForFlight(userFlight):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.query(KeyConditionExpression=Key('route').eq(userFlight.route),
		FilterExpression=Key('flight_key').eq(userFlight.flightKey))
	fares = dynamoResponseToObjects(response)
	fares.sort(key=lambda x: x.fare_validity_date, reverse=False) #todo: dynamodb should return query in sorted order but not working? 
	return fares

def checkAllFares():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan()
	print len(response['Items'])


if __name__ == '__main__':
	checkAllFares()
	