from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta
from helpers import * 
from fares_db import * 

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
		self.usingPoints = item['using_points']
		self.flightKey = item['flight_key']
		self.route = self.origin + "_" + self.destination
		self.fareHistory = []
		self.sentEmail = False
		if ('sent_email' in item):
			self.sentEmail = item['sent_email']

	def __str__(self):
		return "%s -> %s on %s. Paid: %s. #%s." % (self.origin, self.destination, self.date.strftime("%m/%d/%Y"), 
			costString(self.cost, self.usingPoints), self.flightNumber)

	def basicStr(self):
		return "%s -> %s on %s" % (self.origin, self.destination, self.date.strftime("%m/%d/%Y")) 

	def addFares(self, fares):
		for fare in fares:
			self.fareHistory.append(fare)

	def checkRefund(self):
		#returns False for no Refund and a String if there is
		if (len(self.fareHistory) == 0):
			return False
		latestFare = self.fareHistory[-1]
		print(latestFare)
		currentCost = latestFare.points if self.usingPoints else latestFare.price
		if (currentCost < self.cost):
			return "Refund Found! The current cost is %s as of %s" % (costString(currentCost,self.usingPoints), latestFare.fare_validity_date.strftime("%m/%d/%Y")) + "\nFlight info: " + str(self)
		else:
			return False

def dynamoResponseToObjects(response):
	flights = []
	for item in response['Items']:
		flights.append(UserFlight(item))
	return flights

def putUserFlight(flight):
	flight.itemDict['sent_email'] = flight.sentEmail
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	table.put_item(Item= flight.itemDict)

def getUserFlights(username):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.query(KeyConditionExpression=Key('username').eq(username))
	return dynamoResponseToObjects(response)


def getAllFlights():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan()
	return dynamoResponseToObjects(response)

def checkForRefunds():
	flights = getAllFlights()
	for flight in flights:
		print(flight)
		fares = getFaresForFlight(flight)
		flight.addFares(fares)
		refund = flight.checkRefund() 
		if refund:
			if not flight.sentEmail:
				sendEmail(getUser(flight.username).email, 'Southwest Refund Found: ' + flight.basicStr(), refund)
				print(refund)
				flight.sentEmail = True
				putUserFlight(flight)
			else:
				print('Refund found, but already sent email')
		elif not refund and flight.sentEmail:
			flight.sentEmail = False
			putUserFlight(flight)

def countUserFlights():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	return table.item_count

if __name__ == '__main__':
	flights = getAllFlights()
	for flight in flights:
		print(flight)
		fares = getFaresForFlight(flight)
		for fare in fares:
			print(fare)