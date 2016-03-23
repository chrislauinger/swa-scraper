from fares_db import * 
from user_db import *
from userFlights_db import *
from helpers import * 
from privateConstants import * 
from datetime import datetime


flights = getUserFlights('chrislauinger')
for flight in flights:
	if flight.flightNumber == 1126:
		fares = getFaresForFlight(flight)
		for fare in fares:
			print(fare)
