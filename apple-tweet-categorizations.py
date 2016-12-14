from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
from happyfuntokenizing import *
import csv, json, math, nltk

apple_corpus = ['apple', 'itunes', 'ipad', 'ipod', 'mac', 'ios', 'iphone', 'AAPL', 'cupertino', 'safari', 'ilife', 'iwork', 'garageband', 'ibook', 'powerbook', 'itouch', 'app', 'store', 'macworld', 'facetime', 'icloud', 'mobileme', 'siri', 'imovie', 'iphoto', 'quicktime', 'logic pro', 'think different']

def collectData(file):
	f = open(file,'r')
	data = {}
	applebag = []
	nonebag = []
	for line in f:
		words = line.split()
		label = words[0]
		tweet = ' '.join(x for x in words[2:])
		if label == 'apple':
			applebag.append(tweet)
		else:
			nonebag.append(tweet)
	data['apple'] = applebag
	data['none'] = nonebag
	f.close()
	return data

def collecTrainData(file):
	f = open(file, 'r')
	data = []
	for line in f:
		words = line.split()
		label = words[0]
		tweet = ' '.join(x for x in words[2:])
		item = {
			'tweet': tweet,
			'label': label
		}
		data.append(item)
	f.close()
	return data

def cleaning(data):
	#lowering letter
	data = [x.lower() for x in data]
	#replace punctuation
	data = [x.replace('. ',' ') for x in data] 
	data = [x.replace(': ',' ') for x in data]
	data = [x.replace('?',' ') for x in data]
	data = [x.replace('!',' ') for x in data]
	data = [x.replace(';',' ') for x in data]
	data = [x.replace(',',' ') for x in data]
	return data

def stemming(data):
	stemmer = PorterStemmer()
	stemData = []
	for single in data:
		words = single.split()
		singles = [stemmer.stem(unicode(word, errors='replace')) for word in words]
		temp = ' '.join(word for word in singles)
		stemData.append(temp)
	return stemData

def lemmatizing(data):
	lemmatizer = WordNetLemmatizer()
	lemmatizedData = []
	for single in data:
		words = single.split()
		singles = [lemmatizer.lemmatize(unicode(word, errors='replace')) for word in words]
		temp = ' '.join(word for word in singles)
		lemmatizedData.append(temp)
	return lemmatizedData

def twitterTokenizing(data):
	tok = Tokenizer(preserve_case=False)
	tokenizedData = []
	for text in data:
		tokenized = tok.tokenize(text)
		tokenizedData.append(' '.join(token for token in tokenized))
	return tokenizedData

def getIndex(lst, key, val):
	return next(index for (index, d) in enumerate(lst) if d[key] == val)

def tokenizing(data):
	wordbags = []
	for text in data:
		words = text.split()
		for word in words:
			if len(word) > 3:
				if word not in [x['word'] for x in wordbags]:
					item = {
						'word': word,
						'length': len(word),
						'total': 1
					}
					wordbags.append(item)
				else:
					ix = getIndex(wordbags,'word',word)
					wordbags[ix]['total'] += 1
	return wordbags

def addSmooth(data):
	for x in data:
		x['total'] += 1
	return data

def getTotalWord(data):
	total = 0
	for ix in xrange(len(data)):
		total += data[ix]['total']
	return total

def addProbability(data, wordTotal):
	for ix in xrange(len(data)):
		data[ix]['probability'] = float(data[ix]['total'])/float(wordTotal)
	return data

def builModel(dataBags):
	dataBags = addSmooth(dataBags)
	wordTotal = getTotalWord(dataBags)
	dataBags = addProbability(dataBags, wordTotal)
	return dataBags

def getProbFromModel(dataModel, word):
	prob = 0
	for ix in xrange(len(dataModel)):
		if word == dataModel[ix]['word']:
			prob = dataModel[ix]['probability']
			break
	return prob

def testing(dataTrain, appleModel, noneModel):
	truePredict = 0
	for data in dataTrain:
		words = data['tweet'].split()
		appleProb = 0
		noneProb = 0
		for word in words:
			appleProb += getProbFromModel(appleModel, word)
			noneProb += getProbFromModel(noneModel, word)
		predict = "apple" if appleProb > noneProb else "none"
		predicting = True if predict == data['label'] else False
		if predicting:
			truePredict += 1
		print '%s diklasifikasikan ke %s dan hasil %s' % (data['tweet'], predict, predicting)
	accuracy = float(truePredict) / float(len(dataTrain)) * 100
	print 'Hasil akurasi = %f %' % accuracy	

def training(data):
	print '\n === Cleaning === \n'
	data = cleaning(data)
	# print '\n === stemming === \n'
	# data = stemming(data)
	# print '\n === Twitter Tokenizing === \n'
	# data = twitterTokenizing(data)
	print '\n === Lemmatization === \n'
	data = lemmatizing(data)
	print '\n === Tokenizations === \n'
	data = tokenizing(data)
	print '\n === Build Model === \n'
	model = builModel(data)
	return model

print '\n === Collecting === \n'
data = collectData('filtered-training.txt')
apple_data = data['apple']
none_data = data['none']
dataTrain = collecTrainData('filtered-testing.txt')

appleModel = training(apple_data)
noneModel = training(none_data)

testing(dataTrain, appleModel, noneModel)