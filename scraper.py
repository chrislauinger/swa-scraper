from swa import *
from swa.spiders.swa_spider import *
import swa.settings

from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

from scrapy import signals
from scrapy.exporters import JsonItemExporter

from datetime import datetime, timedelta
from itertools import permutations
import time 

def runUserFlights(userFlights):
	a = time.time()
	process = CrawlerProcess(get_project_settings())
	for flight in userFlights:
		process.crawl(SWAFareSpider, fromCity = flight.origin, days = 1, 
			toCity = flight.destination, startDate = flight.date)		
	d = process.join()
	d.addBoth(lambda _: reactor.stop())
	reactor.run() # the script will block here until all crawling jobs are finished
	print("crawl time: " + str(time.time() - a))

def runAllCities(cities, days):
	a = time.time()
	process = CrawlerProcess(get_project_settings())
	for pair in permutations(cities,2):
		process.crawl(SWAFareSpider, fromCity = pair[0], days = days, toCity = pair[1])		
	d = process.join()
	d.addBoth(lambda _: reactor.stop())
	reactor.run() # the script will block here until all crawling jobs are finished
	print("crawl time: " + str(time.time() - a))

if __name__ == '__main__':
	cities =  ['SEA','BWI','SAN','MDW','DEN','HOU','LAX','SFO','OAK','PDX'] # majors
	days = 180
	runAllCities(cities, days)
	#takes about 2 hours to run 90 routes for 180 days 
	#TODO: use multiple reactor runs to run more than 90 routes (times out with too many spiders in one run)
