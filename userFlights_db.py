from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta
from helpers import * 
from fares_db import getFaresForFlight
from user_db import getUser  

import boto3
from boto3.dynamodb.conditions import Key, Attr 

TABLE_NAME = 'userFlights'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'


class UserFlight():
	def __init__(self, item):
		self.itemDict = item
		self.username = item['username']
		self.origin = item['origin'] 
		self.date = fromMsEpoch(int(item['date']))
		self.destination = item['destination']
		self.flightNumber = item['flight_number']
		self.cost = item['cost']
		self.usingPoints = False
		if (self.cost > 1000):
			self.usingPoints = True
		self.flightKey = item['flight_key']
		self.route = self.origin + "_" + self.destination
		self.fareHistory = []
		self.maxDrop = 0
		if ('max_drop' in item):
			self.maxDrop = item['max_drop']

	def __str__(self):
		return "%s paid %s for %s -> %s (#%s) on %s" % (self.username, costString(self.cost, self.usingPoints), self.origin, self.destination, self.flightNumber, self.date.strftime("%m/%d/%Y")) 

	def basicStr(self):
		return "%s -> %s on %s" % (self.origin, self.destination, self.date.strftime("%m/%d/%Y")) 

	def addFares(self, fares):
		for fare in fares:
			self.fareHistory.append(fare)

	def checkRefund(self):
		#returns False for no Refund a number for the diff 
		if (len(self.fareHistory) == 0):
			return False
		latestFare = self.fareHistory[-1]
		currentCost = latestFare.points if self.usingPoints else latestFare.price
		if (currentCost < self.cost):
			diff = diffCostString(currentCost, self.cost, self.usingPoints)
			return diff 
		else:
			return False

def dynamoResponseToObjects(items):
	flights = []
	for item in items:
		flights.append(UserFlight(item))
	return flights

def putUserFlight(flight):
	flight.itemDict['max_drop'] = flight.maxDrop
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	table.put_item(Item= flight.itemDict)

def getUserFlights(username):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.query(KeyConditionExpression=Key('username').eq(username))
	items = response['Items']
	while(response.has_key('LastEvaluatedKey')):
		response = table.query(KeyConditionExpression=Key('username').eq(username), ExclusiveStartKey = response['LastEvaluatedKey'])
		items = items + response['Items']
	return dynamoResponseToObjects(items)


def getAllFlights():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan()
	items = response['Items']
	while(response.has_key('LastEvaluatedKey')):
		response = table.scane(ExclusiveStartKey = response['LastEvaluatedKey'])
		items = items + response['Items']
	return dynamoResponseToObjects(items)

def checkForRefunds():
	flights = getAllFlights()
	for flight in flights:
		fares = getFaresForFlight(flight)
		flight.addFares(fares)
		refund = flight.checkRefund()
		print(flight)
		if refund:
			if refund > flight.maxDrop:
				refundStr = "Refund Found! Re-book on southwest.com for a refund of %s\n%s" % (refund,  str(flight))
				sendEmail(getUser(flight.username).email, 'Southwest Refund Found: ' + flight.basicStr(), refundStr)
				print(refund)
				flight.maxDrop = refund
				putUserFlight(flight)
			else:
				print(str(flight) + '-- Refund found, but not a large enough drop')

def countUserFlights():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	return table.item_count

def printFlightsWithoutFares():
	flights = getAllFlights()
	for flight in flights:
		fares = getFaresForFlight(flight)
		if (len(fares) == 0):
			print(flight)


def minPointsFlight():
	minPoints = 5000
	flights = getAllFlights()
	for flight in flights:
		fares = getFaresForFlight(flight)
		for fare in fares: 
			if (fare.points < minPoints):
				minPoints = fare.points
				print(minPoints)



if __name__ == '__main__':
	print(str(printFlightsWithoutFares()))
	#minPointsFlight()