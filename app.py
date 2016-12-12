from pymongo import MongoClient
import csv, datetime, json, logging, time, math
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

def smoothing(obj):
	for ix in range(len(obj)):
		obj[ix]['total'] += 1
	return obj

def wordSelection(word, model):
	if word not in [x['word'] for x in model]:
		obj = {
			'word': word,
			'total': 1
		}
		model.append(obj)
	else:
		ix = getIndex(model,'word',word)
		model[ix]['total'] += 1
	return model

def getProbability(countWord, totalWord):
	return float(countWord) / float(totalWord)

def addProbLog(model, totalWord):
	for ix in range(len(model)):
		prob = getProbability(model[ix]['total'], totalWord)
		model[ix]['probability'] = prob
		model[ix]['ln'] = math.log(prob)
	return model

def modelBuilding(wordbag):
	model = []
	for bag in wordbag:
		if len(bag['word']) > 3:
			model = wordSelection(bag['word'], model)
	model = smoothing(model)
	model = addProbLog(model, len(wordbag))
	return model

def getWordToObjTest(data):
	obj = []
	ix = 0
	for text in data:
		ix += 1
		words = text.split()
		wordbag = []
		for word in words:
			objWord = {
				'word': word,
				'app': 0.00,
				'other': 0.00
			}
			wordbag.append(objWord)
		o = {'id': ix, 'text': text,'wordbag': wordbag}
		obj.append(o)
	return obj

def testing(mandrill, other, test):
	objTest = getWordToObjTest(test)
	for ix in range(len(objTest)):
		for jx in range(len(objTest[ix]['wordbag'])):
			wordObj = objTest[ix]['wordbag'][jx]
			word = wordObj['word']
			for j in range(len(mandrill)):
				if word == mandrill[j]['word']:
					wordObj['app'] = mandrill[j]['ln']
			for j in range(len(other)):
				if word == other[j]['word']:
					wordObj['other'] = other[j]['ln']
	prediction = []
	for x in objTest:
		totalApp = sum([word['app'] for word in x['wordbag']])
		totalOther = sum([word['other'] for word in x['wordbag']])
		predict = "App" if totalApp > totalOther else "Other"
		obj = {
			'id': x['id'],
			'tweet': unicode(x['text'], errors='replace'),
			'predict': predict
		}
		prediction.append(obj)
	return prediction

def writeToJson(file, data):
	j = json.dumps(data, indent=2)
	f = open(file, 'w')
	print >> f,j
	f.close()

mandrill = collectData('../tweet-dataset/Mandrill.csv')
other = collectData('../tweet-dataset/Other.csv')
test = collectData('../tweet-dataset/Test.csv')
# "\n========= cleaning ==========\n"
mandrill = cleaning(mandrill)
other = cleaning(other)
# "\n========= Tokenizations ==========\n"
objMandrill = tokenizations(mandrill)
objOther = tokenizations(other)
# "\n========= Model Building ==========\n"
modelMandrill = modelBuilding(objMandrill)
modelOther = modelBuilding(objOther)

prediction = testing(modelMandrill, modelOther, test)
print prediction
writeToJson('prediction.json', prediction)