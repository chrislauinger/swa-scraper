This is a spider for use with [Scrapy](http://www.scrapy.org) that crawls for and parses fares for one-way flights on Southwest's website. 

# Usage
Install Scrapy and run from the command line:

	scrapy crawl southwestFare -a fromCity=ABC -a toCity=DEF -a days=2 -o output.json -t json 
	
start data base:
mongod --storageEngine=mmapv1 --dbpath C:/DB

#AWS credientials found locally:
/home/chris/.aws/credentials

# Disclaimer
As with any site scraper, this can break. At any moment. If Southwest tweaks their page layout, things might go astray. If you want to tweak anything, a good place to start would be the information selection XPath in `swa/spiders/swa_spider.py`.

#Data info:
Timestamps converted to UTC: 
the date of the flight in fares and userFlights are set to midnight UTC.

The fares are in UTC epoch time, but correspond to local time for the flight.  
For exmaple, to get the depart time of the flight, convert UTC epoch timestamp to date object and display UTC date object. 