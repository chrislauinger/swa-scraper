from swa.items import *
from scrapy.spiders import Spider
from scrapy.http import FormRequest,Request
from scrapy.selector.lxmlsel import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from datetime import datetime, timedelta
from dateutil.parser import parse as dateParse
import re
import itertools, collections
import logging 
from urlparse import urljoin

class Util(object):
	@classmethod
	def parseFlight(_class, string, date, points = None):
		""" General format:
		Departing flight    123(/456)   $0000    12:30AM depart    7:25AM arrive     (Non/1/2)stop    (Change planes in XXX)
		[always]			[flt1/2]    [price]  [departure]       [arrival]   		 [# stops] 		  [connection]
		"""
		removeKeywords = ['Departing flight', 'depart', 'arrive', 'Change Planes in', 'stop', 'stops', 'Plane Change']
		regex = '|'.join(removeKeywords)
		infoList = filter(lambda el: el!="", re.sub(regex, "", string).split(' '))		
		stops = int(infoList[4]) if infoList[4] != 'Non' else 0	
		
		if stops == 0:
			connecting_arpts = []
		elif ( infoList[5] not in SWAFareSpider.cities):
			connecting_arpts = []
		else:
			connecting_arpts = list(infoList[5].split('/'))
		
		departureDT = dateParse("%s %s" % (date, infoList[2]) )
		arrivalDT = dateParse("%s %s" % (date, infoList[3]) )
		if ( arrivalDT < departureDT ): departureDT += timedelta(days=1)
		
		flight = {
			'flight': tuple(infoList[0].split('/')),
			'price': int(infoList[1][1:].replace(",","")),
			'depart': departureDT,
			'arrive': arrivalDT,
			'depart_date' : date,
			'stops': stops,
			'connecting_arpts': connecting_arpts,
			'fare_validity_date': datetime.now(), 
			'points' : int(points.replace(",",""))
		}
		return flight

class SWAFareSpider(Spider):
	"""A spider to scrape the Southwest site for fare pricing."""
	
	FORMNAME = "buildItineraryForm"

	name = "southwestFare"
	start_urls = ['http://www.southwest.com/flight/search-flight.html']
	
	cities = ['GSP', 'FNT', 'BOS', 'OAK', 'LIT', 'BOI', 'SAN', 'DCA', 'LBB', 'BWI', 
	'PIT', 'RIC', 'SAT', 'JAX', 'IAD', 'JAN', 'HRL', 'CHS', 'EYW', 'BNA',
	'PHL', 'SNA', 'SFO', 'PHX', 'LAX', 'MAF', 'LAS', 'CRP', 'CMH', 'FLL', 
	'DEN', 'DTW', 'BUR', 'ROC', 'GEG', 'BUF', 'GRR', 'BDL', 'DSM', 'EWR', 
	'MHT', 'PBI', 'RNO', 'OKC', 'IND', 'ATL', 'ISP', 'SMF', 'BKG', 'PVD', 
	'SEA', 'ECP', 'ICT', 'MDW', 'RDU', 'PDX', 'CLE', 'SJU', 'AUS', 'CLT', 
	'SJC', 'ELP', 'OMA', 'MEM', 'TUS', 'ALB', 'TUL', 'ORF', 'MKE', 'MSY', 
	'MSP', 'CAK', 'TPA', 'DAL', 'DAY', 'ONT', 'STL', 'ABQ', 'HOU', 'SLC', 
	'MCO', 'RSW', 'BHM', 'MCI', 'PNS', 'LGA', 'AMA', 'SDF', 'PWM']
	
	def __init__(self, fromCity=None, days=None, toCity=None, startDate=None, *args, **kwargs):
		super(SWAFareSpider, self).__init__(**kwargs)
		self.origin = fromCity
		self.days = int(days)
		self.daysSearched = 0
		if startDate == None:
			self.currentDate = datetime.now() + timedelta(days=1)
			self.currentDate =  self.currentDate.replace(hour=0, minute=0, second=0, microsecond=0)
		elif type(startDate) == str:
			self.currentDate = dateParse(startDate)
		else:
			self.currentDate = startDate
		self.destination = toCity

	@classmethod
	def lookupCity(_class, cityCode):
		if cityCode in _class.cities:
			return cityCode
		else:
			raise Exception("Invalid city specified.")	

	def buildQuery(self):
		"""Build the POST query string for searching flights."""
		queryData = {}
		queryData["twoWayTrip"] = "false"
		queryData["adultPassengerCount"] = "1"
		queryData["outboundTimeOfDay"] = "ANYTIME"
		queryData["fareType"] = "POINTS"
		queryData["originAirport"] = self.lookupCity(self.origin)
		queryData["destinationAirport"] = self.lookupCity(self.destination)
		queryData["outboundDateString"] = self.currentDate.strftime("%m/%d/%Y")
		queryData["returnAirport"] = ""
		return queryData
		
	def parse(self, response):	
		queryData = self.buildQuery()
		while (self.daysSearched < self.days):
			yield FormRequest.from_response(response, formdata=queryData, formname=self.FORMNAME, callback=self.scrapeFlights, 
				dont_filter = True, meta = {'date' : self.currentDate})
			self.daysSearched = self.daysSearched + 1
			self.currentDate = self.currentDate + timedelta(days=1)
			queryData["outboundDateString"] = self.currentDate.strftime("%m/%d/%Y")

	def scrapeFlights(self, response):
		"""Scrape the flights into a Fare() object."""
		htmlSelector = Selector(response = response)
		errors = htmlSelector.xpath("//ul[@id='errors']/li/text()").extract()
		if (len(errors) > 0 ):
			if "does not offer service" in errors[0]: 
				logging.warning(errors) 
			else: 
				logging.error(errors)
			return

		# Conveniently packaged flight info in string form for form submission
		subpath = '//div[@class="productPricing"]//input/@title'
		selectors = [ 
			'//table[@id="faresOutbound"]//td[@class="price_column "]//div[@class="productPricing"]//input/@title' ,   # business select
			'//table[@id="faresOutbound"]//td[@class="price_column"]//div[@class="productPricing"]//input[contains(@id,"B")]/@title', # anytime
			'//table[@id="faresOutbound"]//td[@class="price_column"]//div[@class="productPricing"]//input[contains(@id,"C")]/@title'  # wanna get away
			]
		points_path = '//div[@class="productPricing"]//label/text()'
		points_selectors = [
			'//table[@id="faresOutbound"]//td[@class="price_column "]' + points_path ,   # business select points
			'//table[@id="faresOutbound"]//td[@class="price_column"]//div[@class="productPricing" and .//input[(contains(@id,"B")) and (@name="outboundTrip")]]//label/text()', # anytime
			'//table[@id="faresOutbound"]//td[@class="price_column"]//div[@class="productPricing" and .//input[(contains(@id,"C")) and (@name="outboundTrip")]]//label/text()' # wanna get away
		]
		fareList = []
		pointsList = []
		for selector in selectors:
			fareList.append( htmlSelector.xpath(selector).extract())
		for selector in points_selectors:
			pointsList.append(htmlSelector.xpath(selector).extract())
		fareType = ["Business Select", "Anytime", "Wanna Get Away"] #assume this order is always descending price if available
		fareTypeIndex = 0
		#verify data integrity when grabbing pointss
		if not (len(fareList) == len(pointsList) and len(list(itertools.chain(*fareList))) == len(list(itertools.chain(*pointsList)))): 
			return
		allFlights = []
		for fareTypeIndex in range(3):
			for flightIndex in range(len(fareList[fareTypeIndex])):
				flightString = fareList[fareTypeIndex][flightIndex]
				if ( flightString[0] == 'D' ):
					logging.debug(flightString)
					flightData = Util.parseFlight(flightString, response.meta['date'], pointsList[fareTypeIndex][flightIndex])
					flight = Fare()		
					for	key in flightData:
						flight[key] = flightData[key]
					flight['origin'] = self.origin
					flight['destination'] = self.destination
					flight['faretype'] = fareType[fareTypeIndex]
					allFlights.append(flight)
		

		for flightIndex in range(len(allFlights)):
			flight = allFlights[flightIndex]
			if flight in allFlights[flightIndex+1:]:
				continue
			else:
				yield flight
					
