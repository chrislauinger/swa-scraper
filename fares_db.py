from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key, Attr 
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

def dynamoResponseToObjects(items):
	fares = []
	for item in items:
		fares.append(Fare(item))
	return fares

def getFaresForFlight(userFlight):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	dateLowerBound = toMsEpoch(userFlight.date)
	dateUpperBound = toMsEpoch(userFlight.date + timedelta(days=1)) 
	print(dateLowerBound)
	print(dateUpperBound)
	response = table.query(KeyConditionExpression=Key('route').eq(userFlight.route) & Key('sort_key').between(str(dateLowerBound),str(dateUpperBound)),
		FilterExpression=Key('flight_key').eq(userFlight.flightKey))
	items = response['Items']
	while(response.has_key('LastEvaluatedKey')):
		response = table.query(KeyConditionExpression=Key('route').eq(userFlight.route) & Key('sort_key').between(str(dateLowerBound),str(dateUpperBound)),
			FilterExpression=Key('flight_key').eq(userFlight.flightKey), ExclusiveStartKey = response['LastEvaluatedKey'])
		items = items + response['Items']
	fares = dynamoResponseToObjects(items)
	fares.sort(key=lambda x: x.fare_validity_date, reverse=False) #todo: dynamodb should return query in sorted order but not working? 
	return fares


def countFares():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	return table.item_count

if __name__ == '__main__':
	countFares()

	