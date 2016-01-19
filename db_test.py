import pymongo

if __name__ == '__main__':
	client = pymongo.MongoClient("localhost", 27017)
	db = client["fares"]
	print(db['SAN_HOU'].find().count())
	print(db.command("dbstats"))
	for fare in db['SAN_HOU'].find():
		print(fare)