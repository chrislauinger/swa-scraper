import boto3
from datetime import datetime, timedelta
from helpers import *
import time

TABLE_NAME = 'fares'
REGION = 'us-west-2'
AWS_URL = 'https://dynamodb.us-west-2.amazonaws.com'

def toMsEpoch(date):
    tt = datetime.timetuple(date)
    sec_epoch_loc = int(time.mktime(tt) * 1000)
    return sec_epoch_loc

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
        itemDict['fare_validity_date'] = toMsEpoch(itemDict['fare_validity_date'])
        itemDict['route'] = itemDict['origin'] + "_" + itemDict['destination']
        itemDict['sort_key'] = str(itemDict['depart']) + "_" + str(itemDict['fare_validity_date']) + "_" + str(itemDict['flight'][0]) #need flight num so sort keys are not the same
        itemDict['flight'] = int(itemDict['flight'][0])
        itemDict['flight_key'] = itemDict['route'] + "_" + str(toMsEpoch(itemDict['depart_date'])) + "_" + str(itemDict['flight'])
        del itemDict['depart_date']
        self.table.put_item(Item= itemDict)
        return item

