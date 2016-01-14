from swa import *
from swa.spiders.swa_spider import *
import swa.settings

from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

class SWACrawlerScript(object):
	def __init__(self, origin, destination, date, debug=False, defaultSettings=True):
		self.debug = debug
		self.origin = origin
		self.destination = destination
		self.date = date
		self.spider = SWAFareSpider(self.origin, self.date, self.destination)
		
		# initialize settings
		settingValues = self.loadSettings() if defaultSettings else dict()
		self.settings = Settings(values=settingValues)

		# initialize crawler
		self.process = CrawlerProcess(self.settings)
		#self.crawler.configure()
		
		print "Set up"
	def loadSettings(self):	
		settingsList = [i for i in dir(swa.settings) if i[0] != "_"]
		settingsDict = {}
		for s in settingsList:
			settingsDict[s] = eval("swa.settings.%s" % s)
		return settingsDict
	
	def run(self):
		print "Running"
		self.process.crawl(self.spider)
		self.process.start()
		reactor.run()

if __name__ == '__main__':
	SWACrawlerScript(origin="OAK", destination="DEN", date="January 16th, 2016", debug=True).run()