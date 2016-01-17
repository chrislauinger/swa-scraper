from swa.items import *
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.selector.lxmlsel import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from datetime import datetime, timedelta
from dateutil.parser import parse as dateParse
import re
import itertools, collections
import logging 


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
			connectingArpts = None
		elif ( infoList[5] not in SWAFareSpider.cities):
			connectingArpts = None
		else:
			connectingArpts = tuple(infoList[5].split('/'))
		
		departureDT = dateParse("%s %s" % (date, infoList[2]) )
		arrivalDT = dateParse("%s %s" % (date, infoList[3]) )
		if ( arrivalDT < departureDT ): departureDT += timedelta(days=1)
		
		flight = {
			'flight': tuple(infoList[0].split('/')),
			'price': infoList[1][1:],
			'depart': departureDT,
			'arrive': arrivalDT,
			'stops': stops,
			'connectingArpts': connectingArpts,
			'fareValidityDate': datetime.now(), 
			'points' : points
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
	
	def __init__(self, fromCity=None, date=None, toCity=None, *args, **kwargs):
		super(SWAFareSpider, self).__init__(**kwargs)
		self.origin = fromCity
		if isinstance(date, datetime):
			self.outDate = date
		else:
			self.outDate = dateParse(date)
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
		queryData["outboundDateString"] = self.outDate.strftime("%m/%d/%Y")
		queryData["returnAirport"] = ""
		return queryData
		
	def parse(self, response):	
		queryData = self.buildQuery()
		return [FormRequest.from_response(response, formdata=queryData, formname=self.FORMNAME, callback=self.scrapeFlights)]

	def scrapeFlights(self, response):
		"""Scrape the flights into a Fare() object."""
		htmlSelector = Selector(response = response)

		if (len(htmlSelector.xpath("//ul[@id='errors']/li/text()").extract()) > 0 ):
			logging.error("Error: %s" % theError)
			return

		# Conveniently packaged flight info in string form for form submission
		subpath = '//div[@class="productPricing"]//input/@title'
		selectors = [ 
			'//table[@id="faresOutbound"]//td[@class="price_column "]' + subpath,   # business select
			'//table[@id="faresOutbound"]//td[@class="price_column"][1]' + subpath, # anytime
			'//table[@id="faresOutbound"]//td[@class="price_column"][2]' + subpath  # wanna get away
			]
		points_path = '//div[@class="productPricing"]//label/text()'
		points_selectors = [
			'//table[@id="faresOutbound"]//td[@class="price_column "]' + points_path ,   # business select points
			'//table[@id="faresOutbound"]//td[@class="price_column"][1]' + points_path, # anytime
			'//table[@id="faresOutbound"]//td[@class="price_column"][2]' + points_path  # wanna get away	
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
					flightData = Util.parseFlight(flightString, self.outDate.date(), pointsList[fareTypeIndex][flightIndex])
					flight = Fare()		
					for	key in flightData:
						flight[key] = flightData[key]
					flight['origin'] = self.origin
					flight['destination'] = self.destination
					flight['date'] = self.outDate
					flight['faretype'] = fareType[fareTypeIndex]
					allFlights.append(flight)
		
		for flightIndex in range(len(allFlights)):
			flight = allFlights[flightIndex]
			if flight in allFlights[flightIndex+1:]:
				continue
			else:
				yield flight
					
