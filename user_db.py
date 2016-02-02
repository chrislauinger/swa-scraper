from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta

import boto3

TABLE_NAME = 'users'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'

class User():
	def __init__(self, username, firstName, lastName, email):
		self.username = username
		self.firstName = firstName
		self.lastName = lastName
		self.email = email

def getUser(userName):
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.get_item(Key={'username': username})
	return response['Item']

def getAllUsernames():
	table = boto3.resource('dynamodb', region_name=REGION, endpoint_url=AWS_URL).Table(TABLE_NAME)
	response = table.scan(AttributesToGet=['username'])
	return response['Items']

if __name__ == '__main__':
	print(getAllUsernames())