#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: Mongodb接口 

数据库数据:
{
	"check_time":"2017-11-1 11:02:03",
	"db":{
		"chinese":"MySQL",
		"name":"mysql",
		"version":"null"
	},
	"geoinfo":{
		"asn": 32475,
		"city": {
			"names": {
				"en": "",
				"zh-CN": ""
			}
		},
		"continent": {
			"code": "EU",
			"names": {
				"en": "Europe",
				"zh-CN": "\u6b27\u6d32"
			}
		},
		"country": {
			"code": "RO",
			"names": {
				"en": "Romania",
				"zh-CN": "\u7f57\u9a6c\u5c3c\u4e9a"
			}
		},
		"location": {
			"lat": 46.0,
			"lon": 25.0
		}
		
	},
	"ip": ["120.14.23.4"],
	"language": "PHP",
	"server":{
		"name":"nginx",
		"version":null
	},
	"site":demo.org,
	"title":"this is a demo site title",
	"webapp":[{
		"name":"wordpress",
		"url":"http://demo.org",
		"version":"4.4.1"
	}],
	"headers":"..."
}


site 为主键
'''
import time
import pymongo
import re
import sys
from pymongo import MongoClient

sys.path.append('..')
from config import PAGE_SIZE

class Mongodb():
	"""docstring for Mongodb"""
	def __init__(self, client=None,host="localhost",port=27017):
		try:
			self.client = MongoClient(host,port) if client is None else client
		except Exception as e:
			raise e
		self.db = self.client['thirdeye']
		self.collection = self.db['matches']
		self.db.collection.create_index([('webapp.name',pymongo.ASCENDING)])
		self.db.collection.create_index([('geoinfo.country.code',pymongo.ASCENDING)])
		self.db.collection.create_index([('geoinfo.city.names',pymongo.ASCENDING)])

	def setitem(self,info_dict):
		"""
		:Parameter:
			- info_dict : 一个网站的完整数据
		"""
		t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
		info_dict.update({'check_time':t})
		# pprint(info_dict)
		site = info_dict.get('site')
		self.collection.update({'site':site},{'$set':info_dict},upsert=True)

	def getitem(self,num=1,skip=0):
		""" 返回网站信息
			:Parameter
				- num: 返回的数据数量,,-1 表示全部
				- skip: 跳过的数据,,适用于翻页功能

			格式:
			{
				"matchs":[{...}],
				"total":"20"
			} 	
		"""
		if num < 0:
			data = self.collection.find().skip(skip)
		else:
			data = self.collection.find().limit(num).skip(skip)

		items = []
		if data:
			for item in data:
				items.append(item)
			d = {
				"matches":items,
				"total": len(items)
			}
			return d
		else:
			raise KeyError() + " Database does not have any data."

	def getcount(self):
		return self.collection.count()
	

	def query(self,query,page=1):
		""" 传进查询的语句
		:Parameter
			- query = {"webapp":"phpcms"}
				- webapp -> webapp.name
				- country -> geoinfo.country.code
				- city -> geoinfo.city.names.en
				- language -> language
		e.x : query({"webapp":"phpcms",'country':'cn','city':'beijing'})

			- return : d = {'matches':[{..},..],"total": 200}
		"""
		_query = {}
		record = []
		if 'webapp' in query.keys():
			_q = re.compile(query['webapp'],re.I)
			_query['webapp.name'] = _q
		if 'country' in query.keys():
			_q = re.compile(query['country'],re.I)
			_query['geoinfo.country.code'] = _q
		if 'city' in query.keys():
			_q = re.compile(query['city'],re.I)
			_query['geoinfo.city.names.en'] = _q
		if 'language' in query.keys():
			_q = re.compile(query['language'],re.I)
			_query['language'] = _q

		if len(_query) == 0:
			return record	

		total = self.collection.find(_query,{"_id":0}).count()
		data = self.collection.find(_query,{"_id":0}).sort('_id').limit(PAGE_SIZE).skip((page-1)*PAGE_SIZE)
		for item in data:
			record.append(item)
		d = {"matches":record,'total':data.count()}
		return d


	def dropcollection(self):
		dataNum = self.collection.count()
		self.collection.drop()
		return dataNum

def main():
	mongo = Mongodb()
	# mongo.query({'geoinfo.country.code':re.compile('cn',re.I),'webapp.name':re.compile('phpcms',re.I)})
	# mongo.query({'geoinfo.city.names.en':re.compile('beijing',re.I)})
	
	mongo.query({"webapp":"phpcms"})
	

if __name__ == '__main__':
	main()

