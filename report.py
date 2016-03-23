from fares_db import * 
from user_db import *
from userFlights_db import *
from helpers import * 
from privateConstants import * 
from datetime import datetime

# TODO: grep out logs for scraper, runUserFares and Email (once running)


usernames = getAllUsernames()
usersNoFlights = 0
usernameRank = []
for username in usernames:
	flights = getUserFlights(username)
	usernameRank.append((username, len(flights)))
	if len(flights) == 0:
		usersNoFlights = usersNoFlights + 1
usernameRank = sorted(usernameRank, key=lambda tup: tup[1], reverse = True)

def countFlightsWithoutFares():
	flights = getAllFlights()
	count = 0
	for flight in flights:
		fares = getFaresForFlight(flight)
		if (len(fares) == 0):
			count = count + 1
	return count

flights = countUserFlights()
users = countUsers()

flightsNoFaresPerc = 100.0 * float(countFlightsWithoutFares()) / float(flights)
usersNoFlightsPerc =  100.0 * float(usersNoFlights) / float(users)


email_str = "Fares: %s\nUsers: %s\nUserFlights: %s \n\nUsers with no flight: %s \nFlights with no fares: %s" % ("{:,}".format(countFares()), "{:,}".format(users), "{:,}".format(flights), "{:10.1f}".format(usersNoFlightsPerc), "{:10.1f}".format(flightsNoFaresPerc)) + "\n"

i = 0
for item in usernameRank:
	i = i + 1
	email_str = email_str + "\n" + item[0] + ": " + str(item[1])
	if i > 5: 
		break

subject = "Daily Report: %s" % (datetime.now().strftime("%m/%d/%Y"))
print(email_str)
sendEmail(reportEmail, subject, email_str)
