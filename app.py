from pymongo import MongoClient
import csv, json, datetime, logging, time
import logging.handlers

client = MongoClient()
db = client.tweets

def collectData(file):
	f = open(file, 'rU')
	reader = csv.reader(f)
	data = []
	i = 0
	for line in reader:
		if len(line) == 0:
			break
		if i != 0:
			data.append(line[0])
		i+=1
	f.close()
	return data

def cleaning(data):
	data = [x.lower() for x in data] #lowering letter
	#replace punctuation
	data = [x.replace('. ',' ') for x in data] 
	data = [x.replace(': ',' ') for x in data]
	data = [x.replace('?',' ') for x in data]
	data = [x.replace('!',' ') for x in data]
	data = [x.replace(';',' ') for x in data]
	data = [x.replace(',',' ') for x in data]
	return data

def tokenizations(data):
	wordbag = []
	for text in data:
		words = text.split()
		for word in words:
			bag = {
				'word': word,
				'length': len(word)
			}
			wordbag.append(bag)
	return wordbag

def getIndex(lst, key, val):
	return next(index for (index, d) in enumerate(lst) if d[key] == val)

def modelBuilding(wordbag):
	model = []
	for bag in wordbag:
		if len(bag['word']) > 3:
			if bag['word'] not in [x['word'] for x in model]:
				obj = {
					'word': bag['word'],
					'total': 1
				}
				model.append(obj)
			else:
				ix = getIndex(model,'word',bag['word'])
				model[ix]['total'] += 1
	return model
mandrill = collectData('../tweet-dataset/Mandrill.csv')
print mandrill
print "\n========= cleaning ==========\n"
mandrill = cleaning(mandrill)
print mandrill
print "\n========= Tokenizations ==========\n"
objMandrill = tokenizations(mandrill)
print objMandrill
print "\n========= Model Building ==========\n"
modelMandrill = modelBuilding(objMandrill)
print modelMandrill