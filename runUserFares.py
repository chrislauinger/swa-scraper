from scraper import runUserFlights
import pymongo
from dateutil.parser import parse as dateParse
from datetime import datetime, timedelta
import swa.settings as settings
from swa.items import *
from userFlights_db import * 

if __name__ == '__main__':
	flights = getAllFlights()
	runUserFlights(flights)