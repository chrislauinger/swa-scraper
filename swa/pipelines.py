import pymongo
import boto3
from datetime import datetime, timedelta
import time

TABLE_NAME = 'fares'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'

def toMsEpoch(date):
    tt = datetime.timetuple(date)
    sec_epoch_loc = int(time.mktime(tt) * 1000)
    return sec_epoch_loc


class MongoPipeline(object):

    def __init__(self, mongo_server, mongo_port, mongo_db):
        self.mongo_server = mongo_server
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_server=crawler.settings.get('MONGODB_SERVER'),
            mongo_port=crawler.settings.get('MONGODB_PORT'),
            mongo_db=crawler.settings.get('MONGODB_DB'), 
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_server, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
    	collection = spider.origin + "_" + spider.destination
        self.db[collection].insert(dict(item))
        return item

class DynamoPipeline(object):

    def __init__(self, aws_url, aws_region, table_name):
        self.aws_url = aws_url
        self.aws_region = aws_region
        self.table_name = table_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            aws_url=crawler.settings.get('AWS_URL'),
            aws_region=crawler.settings.get('AWS_REGION'),
            table_name=crawler.settings.get('DYNAMO_TABLE_NAME'), 
        )

    def open_spider(self, spider):
        self.table = boto3.resource('dynamodb', region_name=self.aws_region, endpoint_url=self.aws_url).Table(self.table_name)

    #def close_spider(self, spider):


    def process_item(self, item, spider):
        #convert datetimes
        itemDict = dict(item)
        itemDict['arrive'] = toMsEpoch(itemDict['arrive'])
        itemDict['depart'] = toMsEpoch(itemDict['depart'])
        itemDict['fareValidityDate'] = toMsEpoch(itemDict['fareValidityDate'])
        itemDict['route'] = itemDict['origin'] + "_" + itemDict['destination']
        itemDict['sort_key'] = str(itemDict['depart']) + "_" + str(itemDict['fareValidityDate'])
        itemDict['flight'] = int(itemDict['flight'][0])
        self.table.put_item(Item= itemDict)
        return item

