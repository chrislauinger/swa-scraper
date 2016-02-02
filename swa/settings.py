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
DOWNLOAD_DELAY = 0.25
DOWNLOAD_TIMEOUT = 100
TELNETCONSOLE_PORT = None #dynamically assign ports
LOG_LEVEL = "ERROR"
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_IP = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_DEBUG = True

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = "" 


USER_AGENT = " "

ITEM_PIPELINES = {'swa.pipelines.DynamoPipeline' : 100 } 

#mongo db settings
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "fares"
#MONGODB_COLLECTION = "" 
#collections are names using origin city then destination city code (ex: OAK_LAX)

#dynamo db settings
DYNAMO_TABLE_NAME = 'fares'
AWS_REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'