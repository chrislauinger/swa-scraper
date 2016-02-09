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

def dynamoResponseToObjects(response):
	users = []
	for item in response['Items']:
		users.append(User(item))
	return users

def getUser(username):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.get_item(Key= {'username' : username})
	return User(response['Item'])

def getAllUsernames():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan(AttributesToGet=['username'])
	return dynamoResponseToObjects(response)

if __name__ == '__main__':
	print(getAllUsernames())