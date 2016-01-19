# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Fare(Item):
	origin = Field()
	destination = Field()
	flight = Field()
	arrive = Field()
	depart = Field()
	faretype = Field()
	price = Field()
	points = Field()
	stops = Field()
	connectingArpts = Field()
	fareValidityDate = Field() 

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return (self['flight'] == other['flight'] and self['depart'] == other['depart'])
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)
