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

flights = getAllFlights()
flightsNoFares = 0
for flight in flights:
	fares = getFaresForFlight(flight)
	if (len(fares) == 0):
		flightsNoFares = flightsNoFares + 1

flightCount = countUserFlights()
users = countUsers()
fares = countFares()

flightsNoFaresPerc = 100.0 * float(flightsNoFares) / float(flightCount)
usersNoFlightsPerc =  100.0 * float(usersNoFlights) / float(users)

email_str = "Fares: %s\nUsers: %s\nUserFlights: %s \n\nPercent users with no flight: %s%%\nPercent flights with no fares: %s%%" % ("{:,}".format(fares), "{:,}".format(users), "{:,}".format(flightCount), "{:10.1f}".format(usersNoFlightsPerc), "{:10.1f}".format(flightsNoFaresPerc)) + "\n"

############### Display top 5 users ##################

i = 0
for item in usernameRank:
	i = i + 1
	email_str = email_str + "\n" + item[0] + ": " + str(item[1])
	if i > 5: 
		break


############# Display top 5 flights with stalest fares ###############
email_str = email_str + "\n" 
times = []
nowtime = datetime.now()
for flight in flights:
	if flight.date < (datetime.now() +  timedelta(days=3)): #close flight
		continue
	fares = getFaresForFlight(flight)
	if len(fares) > 0:
		diff = nowtime - fares[-1].fare_validity_date
		times.append((flight,diff))

times = sorted(times, key=lambda a: a[1], reverse = True)

a = 1
for t in times:
	email_str = email_str + "\n" + str(t[0]) + ": " + str(t[1])
	a = a + 1
	if a > 5:
		break

subject = "Daily Report: %s" % (datetime.now().strftime("%m/%d/%Y"))
print(email_str)
sendEmail(reportEmail, subject, email_str)
