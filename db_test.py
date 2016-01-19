import pymongo
from itertools import permutations

if __name__ == '__main__':
	client = pymongo.MongoClient("localhost", 27017)
	db = client["fares"]
	cities =  ['SEA','BWI','SAN','MDW','DEN','HOU','LAX','SFO','OAK','PDX']
	for pair in permutations(cities,2):
		combo = '%s_%s' % (pair[0], pair[1])
		print(combo + " " + str(db[combo].find().count()))
