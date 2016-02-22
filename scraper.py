from swa import *
from swa.spiders.swa_spider import *
import swa.settings

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

from scrapy import signals
from scrapy.exporters import JsonItemExporter

from datetime import datetime, timedelta
from itertools import permutations
import time 


CITIES =  ['SEA','BWI','SAN','MDW','DEN','HOU','LAX','SFO','OAK','PDX']
#CITIES = ['PVD','BWI']
def getCityPairs():
	return permutations(CITIES,2)

def runUserFlights(userFlights):
	a = time.time()
	process = CrawlerProcess(get_project_settings())
	for flight in userFlights:
		if flight.date > datetime.now(): #check in timezone of flight..
			print(flight)
			process.crawl(SWAFareSpider, fromCity = flight.origin, days = 1, toCity = flight.destination, startDate = flight.date)		
	d = process.join()
	d.addBoth(lambda _: reactor.stop())
	reactor.run() # the script will block here until all crawling jobs are finished
	print("crawl time: " + str(time.time() - a))

def runAllCities(cityPairs, days):
	a = time.time()
	process = CrawlerProcess(get_project_settings())
	for pair in cityPairs:
		process.crawl(SWAFareSpider, fromCity = pair[0], days = days, toCity = pair[1])		
	d = process.join()
	d.addBoth(lambda _: reactor.stop())
	reactor.run() # the script will block here until all crawling jobs are finished
	print("crawl time: " + str(time.time() - a))



def runAllCitiesSeq(cityPairs, days):
	a = time.time()
	runner = CrawlerRunner(get_project_settings())

	@defer.inlineCallbacks
	def crawl():
		for pair in cityPairs:
			yield runner.crawl(SWAFareSpider, fromCity = pair[0], days = days, toCity = pair[1])
   		reactor.stop()
	crawl()
	reactor.run() # the script will block here until the last crawl call is finished
	print("crawl time: " + str(time.time() - a))

if __name__ == '__main__':
	days = 180
	runAllCitiesSeq(getCityPairs(), days)