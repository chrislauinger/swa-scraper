import pymongo

if __name__ == '__main__':
	client = pymongo.MongoClient("localhost", 27017)
	db = client["fares"]
	print(db['SFO_DEN'].find().count())
	print(db['DEN_SFO'].find().count())
	print(db.command("dbstats"))
	#for fare in db['fares'].find({"connectingArpts" : "LAS"}):
	#	print(fare)