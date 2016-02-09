import pymongo
from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta

#TODO: cron script to run after daily scrape

def checkDB(timedelta):
	#prints number of fares found in DB withing timedelta for each route
	client = pymongo.MongoClient(settings.MONGODB_SERVER, settings.MONGODB_PORT)
	db = client[settings.MONGODB_DB]
	start = datetime.now() - timedelta
	total = 0
	print("Fare count back %s days" % timedelta.days)
	for pair in getCityPairs():
		combo = '%s_%s' % (pair[0], pair[1])
		count = db[combo].find({'fareValidityDate': {'$gte': start}}).count()
		total = total + count
		print(combo + " " + str(count))
	print("total " + str(total))

if __name__ == '__main__':
	checkDB(timedelta(days=10))
