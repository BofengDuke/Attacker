#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: 获取web信息
'''

import geoip2.database
import urllib
import socket
from module.webfingerprint import webfingerprint
from module.mongodb import Mongodb
from pprint import pprint

import sys
sys.path.append("/lib")

class Webinfo():
	"""docstring for Webinfo"""
	def __init__(self, url = None):
		"""	
		:Parameter:
			- url:  http://demo.org
		"""
		
		self.url = url
		self.domain = urllib.parse.urlparse(url).hostname

	def save_to_database(self,url):
		self.url = url
		self.domain = urllib.parse.urlparse(url).hostname
		data = {}
		data['db'] = self.get_db()
		data['geoinfo'] = self.get_geoip_info()
		data['ip'] = self.get_ip()

		webf = webfingerprint(self.url)
		data['language'] = webf.get_language()
		data['server'] = webf.get_server()
		data['site'] = self.domain
		data['title'] = webf.get_title()
		data["webapp"] = webf.get_webapp()
		data['header'] = webf.get_header()

		mongo = Mongodb()
		mongo.setitem(data)

	def get_geoip_info(self):
		geoinfo = {}
		try:
			ip = self.get_ip()[0]
		except Exception as e:
			print('Can not get ip by %s'%self.domain)
			print(e)
			return None
		reader = geoip2.database.Reader('lib/GeoLite2-City.mmdb')
		r = reader.city(ip)
		city = {
			"names":{
				"en": r.city.names.get('en',''),
				"zh-CN":r.city.names.get('zh-CN','')
			}
		}
		continent = {
			"code":r.continent.code,
			"names":{
				'en': r.continent.names['en'],
				'zh-CN': r.continent.names['zh-CN']
			}
		}
		country = {
			'code': r.country.iso_code,
			'names': {
				'en': r.country.names['en'],
				'zh-CN': r.country.names['zh-CN']
			}
		}
		location = {
			"lat" : r.location.latitude,
			"lon" : r.location.longitude
		}

		reader.close()

		geoinfo = {
			"asn": "",
			"city":city,
			"continent":continent,
			"country":country,
			"location":location
		}

		return geoinfo

	def get_ip(self):
		""" 一个域名可能对应多个IP
		"""
		iplist = socket.gethostbyname_ex(self.domain)[2]
		return iplist

	def get_db(self):
		db = {}
		db['chinese'] = ""
		db['name'] = ""
		db['version'] = ""
		return db


def main():
	url = "http://dukebf.org"
	webinfo = Webinfo()
	# webinfo.get_geoip_info()
	
	webinfo.save_to_database(url)


if __name__ == '__main__':
	main()