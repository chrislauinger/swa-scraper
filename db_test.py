import pymongo

if __name__ == '__main__':
	#SWACrawlerScript(origin="OAK", destination="DEN", date="01/23/2016").run()
	client = pymongo.MongoClient("localhost", 27017)
	db = client["fares"]
	print(db['OAK_DEN'].find().count())
	print(db.command("dbstats"))
	#for fare in db['fares'].find({"connectingArpts" : "LAS"}):
	#	print(fare)