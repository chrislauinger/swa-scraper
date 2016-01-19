This is a spider for use with [Scrapy](http://www.scrapy.org) that crawls for and parses fares for one-way flights on Southwest's website. 

# Usage
Install Scrapy and run from the command line:

	scrapy crawl southwestFare -a fromCity=ABC -a toCity=DEF -a days=2 -o output.json -t json 
	
start data base:
mongod --storageEngine=mmapv1 --dbpath C:/DB

# Disclaimer
As with any site scraper, this can break. At any moment. If Southwest tweaks their page layout, things might go astray. If you want to tweak anything, a good place to start would be the information selection XPath in `swa/spiders/swa_spider.py`.

