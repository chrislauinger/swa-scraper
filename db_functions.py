from fares_db import * 
from user_db import *
from userFlights_db import *
from helpers import * 
from privateConstants import * 
from datetime import datetime


# flights = getUserFlights('chrislauinger')
# for flight in flights:
# 	if flight.flightNumber == 1126:
# 		fares = getFaresForFlight(flight)
# 		for fare in fares:
# 			print(fare)

flights = getAllFlights()
times = []
nowtime = datetime.now()
for flight in flights:
	if flight.date < (datetime.now() +  timedelta(days=2)): #close flight
		continue
	fares = getFaresForFlight(flight)
	if len(fares) > 0:
		diff = nowtime - fares[-1].fare_validity_date
		times.append((flight,diff))

times = sorted(times, key=lambda a: a[1], reverse = True)

a = 1
for t in times:
	print(t[0])
	print(t[1])
	a = a + 1
	if a > 20:
		break