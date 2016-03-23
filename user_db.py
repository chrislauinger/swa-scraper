from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key, Attr 

TABLE_NAME = 'users'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'

class User():
	def __init__(self, item):
		self.username = item['username']
		self.firstName = item['first_name']
		self.lastName = item['last_name']
		self.email = item['email']

def getUser(username):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.get_item(Key= {'username' : username})
	return User(response['Item'])

def getAllUsernames():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan(AttributesToGet=['username'])
	items = response['Items']
	while(response.has_key('LastEvaluatedKey')):
		response = table.scan(AttributesToGet=['username'], ExclusiveStartKey = response['LastEvaluatedKey'])
		items = items + response['Items']
	usernames = []
	for item in items:
		usernames.append(item['username'])
	return usernames

def countUsers():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	return table.item_count

if __name__ == '__main__':
	print(getAllUsernames())