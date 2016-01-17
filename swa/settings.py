# Scrapy settings for swa project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'swa'

SPIDER_MODULES = ['swa.spiders']
NEWSPIDER_MODULE = 'swa.spiders'
DEFAULT_ITEM_CLASS = 'swa.items.Fare'


USER_AGENT = " "

ITEM_PIPELINES = {'swa.pipelines.MongoPipeline' : 100 } 

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "fares"
#MONGODB_COLLECTION = "" 
#collections are names using origin city then destination city code (ex: OAK_LAX)