import json

def getBooksData(genre, authors, publisher):
	'''reads books_data.json and returns books db data'''
	f=open("db/books_data.json","r")
	s=f.read()
	books_dict = json.loads(s)
	try:
		genre=books_dict[genre]
	except KeyError:
		return None
	
	try:
		authors=genre[authors]
	except KeyError:
		return None

	try:
		publisher=authors[publisher]
	except KeyError:
		return None

	return publisher['book']

def getRestaurantData(location, cuisine, category):
	'''reads restaurant_data.json and returns restaurants db data'''
	f=open("db/restaurant_data.json","r")
	s=f.read()
	#print(s)
	res_dict = json.loads(s)
	#print(res_dict)
	#return res_dict[location][cuisine][category]['mobiles']
	try:
		locations=res_dict[location]
	except KeyError:
		return None
	
	try:
		cuisines=locations[cuisine]
	except KeyError:
		return None

	try:
		categories=cuisines[category]
	except KeyError:
		return None

	return categories['restaurants']