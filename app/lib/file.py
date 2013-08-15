# set of utilities to interact with files

# @author: rm3086 (at) columbia (dot) edu

import csv, shutil, os, glob, cPickle
from log import slogger

log = slogger ('etacts-file')

# read an object (list, dictionary, set) from a serialized file
def read_obj (filename):
	try:
		data = cPickle.load (open(filename, 'rb'))
		return data
	except Exception as e:
		log.error(e)
		return None


# write an object (list, set, dictionary) to a serialized file
def write_obj (filename, data):
	try:
		cPickle.dump(data, open(filename, 'wb'))
		return True
	except Exception as e:
		log.error(e)
		return False

# read data from a csv file    
def read_csv (filename, logout = True):
	try:
		reader = csv.reader (open(filename, "r"))
		data = []
		for r in reader:
			data.append(r)
		return data
	except Exception as e:
		if logout is True:
			log.error(e)
		return None


# read a text file
def read_file (filename, logout = True):
	try:
		fid = open(filename, 'r')
		data = []
		for line in fid:			
			if len(line) > 0:
				data.append (line.strip())		
		fid.close()
		return data
	except Exception as e:
		if logout is True:
			log.error(e)
		return None


# write data to a csv file
def write_csv (filename, data, logout = True):
	try:
		doc = csv.writer (open(filename, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		for d in data:
			doc.writerow (d)
		return True			
	except Exception as e:
		if logout is True:
			log.error(e)
		return False
