This is a spider for use with [Scrapy](http://www.scrapy.org) that crawls for and parses fares for one-way flights on Southwest's website. 

# Usage
Install Scrapy and run from the command line:

	scrapy crawl southwestFare -a fromCity=ABC -a toCity=DEF -a days=2 -o output.json -t json 
	
Or, you can run the crawler using the Scrapy [API](https://scrapy.readthedocs.org/en/latest/topics/api.html), with an example seen in `scraper.py`.
Just instantiate a new SWAFareSpider object with `fromCity, toCity` and `date`. `date` can be a string with any common date representation, as it's automatically parsed.

The crawler records the following information for each fare: origin, destination, flight numbers, price, stops, connecting airports, date, and fare validity date.

# Disclaimer
As with any site scraper, this can break. At any moment. If Southwest tweaks their page layout, things might go astray. If you want to tweak anything, a good place to start would be the information selection XPath in `swa/spiders/swa_spider.py`.

