from fares_db import * 
from user_db import *
from userFlights_db import *
from helpers import * 
from privateConstants import * 
from datetime import datetime

# TODO: grep out logs for scraper, runUserFares and Email (once running)

email_str = "Fares: %s\nUsers: %s\nUserFlights: %s" % ("{:,}".format(countFares()), "{:,}".format(countUsers()), "{:,}".format(countUserFlights()))
subject = "Daily Report: %s" % (datetime.now().strftime("%m/%d/%Y"))
print(email_str)
sendEmail(reportEmail, subject, email_str)
