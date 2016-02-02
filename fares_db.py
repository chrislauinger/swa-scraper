import pymongo
from itertools import permutations
from scraper import * 
import swa.settings as settings
from datetime import datetime, timedelta

#checks dynamo db for fares
#TODO: cron script to run after daily scrape

