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
			if(len(word)>3):
				bag = {
					'word': word,
					'length': len(word)
				}
				wordbag.append(bag)
	return wordbag

mandrill = collectData('../tweet-dataset/Mandrill.csv')
print mandrill
print "\n========= cleaning ==========\n"
mandrill = cleaning(mandrill)
print mandrill
objMandrill = tokenizations(mandrill)
print objMandrill