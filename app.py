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

mandrill = collectData('../tweet-dataset/Mandrill.csv')
print mandrill