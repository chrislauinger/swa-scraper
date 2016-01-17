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

class SWACrawlerScript(object):
	def __init__(self, origin, destination, date):
		self.origin = origin
		self.destination = destination
		self.date = date
		self.process = CrawlerProcess(get_project_settings())
	
	def run(self):
		self.process.crawl(SWAFareSpider, fromCity = self.origin, date = self.date, toCity = self.destination)
		self.process.start()

def runAllCitiesForAllDates(cities, dates):
	#TODO: what's the limit on number of spiders to run, how to run in parrallel
	a = time.time()
	process = CrawlerProcess(get_project_settings())
	for pair in permutations(cities,2):
		for date in dates:
			process.crawl(SWAFareSpider, fromCity = pair[0], date = date, toCity = pair[1])
	d = process.join()
	d.addBoth(lambda _: reactor.stop())
	reactor.run() # the script will block here until all crawling jobs are finished
	print("crawl time: " + str(time.time() - a))

if __name__ == '__main__':
	cities = ['ATL','AUS','BWI','BOS','MDW','DEN','HOU','LAS','LAX','EWR','FLL',
	'OAK','ONT','PHX','PDX','PVD','SLC','SAN','SFO','IAD'] #20 majors
	dates = []
	for i in range(1,2):
		dates.append(datetime.now() + timedelta(days=i))
	runAllCitiesForAllDates(cities, dates)