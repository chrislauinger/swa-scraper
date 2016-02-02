from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta
from helpers import * 

import boto3
from boto3.dynamodb.conditions import Key, Attr

TABLE_NAME = 'userFlights'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'


class UserFlight():
	def __init__(self, item):
		self.username = item['username']
		self.origin = item['origin'] 
		self.date = fromMsEpoch(int(item['date']))
		print(self.date)
		self.destination = item['destination']
		self.flightNumber = item['flight_number']
		self.cost = item['cost']
		self.usingPoints = item['using_points']

	def __str__(self):
		return "%s: %s -> %s on %s. Cost: %s%s %s. #%s." % (self.username, self.origin, self.destination, self.date.strftime("%m/%d/%Y"), 
			"$" if not self.usingPoints else "", self.cost, "points" if self.usingPoints else "", self.flightNumber) 

def dynamoResponseToObjects(response):
	flights = []
	for item in response['Items']:
		flights.append(UserFlight(item))
	return flights

def getUserFlights(username):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.query(KeyConditionExpression=Key('username').eq(username))
	return dynamoResponseToObjects(response)


def getAllFlights():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan()
	return dynamoResponseToObjects(response)

if __name__ == '__main__':
	flights = getAllFlights()
	for flight in flights:
		print(flight)