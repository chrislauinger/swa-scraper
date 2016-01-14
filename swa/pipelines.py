# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

'''
from items import Fare
from scrapy import signals
from scrapy.exceptions import DropItem
from datetime import datetime as dt
import sqlite3 

class CheckDuplicatesPipeline(object):
	def __init__(self):
		self.seen = set()

	def process_item(self, item, spider):
		if ( isinstance(item, Fare) and item['flight'] in self.seen):
			raise DropItem("Duplicate caught.")	
		else:
			self.seen.add(item['flight'])
			return item	

class InsertDBPipeline(object):
	def __init__(self):
		self.conn = sqlite3.connect('swa.db')
		self.c = self.conn.cursor()
		
	def process_item(self, item, spider):
		query = "INSERT INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		data = (dt.now(), item["date"], item["origin"], item["destination"], 
				str(item["flight"]), item["arrive"], item["depart"], 
				int(item["price"]), int(item["stops"]),
				str(item["connectingArpts"]) )
		if ( isinstance(item, fare) ):
			self.c.execute(query, data)
			self.conn.commit()
		self.conn.close()	
			
'''