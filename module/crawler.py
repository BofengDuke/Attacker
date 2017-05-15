#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: 爬虫模块,可以从百度,钟馗之眼爬取链接和主机


'''

import requests,urllib
import lxml.html
import json
import sys
sys.path.append('.')

from module.mongodb import Mongodb
from pprint import pprint
from module.webinfo import Webinfo
from module.decorators import async

class Crawler(object):
	"""docstring for crawler"""
	def __init__(self):
		self.mongodb = Mongodb()

	@async
	def baidu_crawler(self,query,max_page=2):
		# url = "http://www.baidu.com/s?wd="+keyword+"&pn="+str(i * page_number)
		page_number = 10
		url_list = []
		for i in range(max_page):
			baidu_url = "http://www.baidu.com/s?wd="+query+"&pn="+str(i * page_number)
			r = requests.get(baidu_url)
			r.encoding = r.apparent_encoding
			tree = lxml.html.fromstring(r.text)
			links = tree.cssselect('#content_left .t a')
			for link in links:
				try:
					_url = link.get('href')
					if _url.startswith('http://') or _url.startswith('https://'):
						_u = requests.get(_url).url
						_u = self._rm_param(_u)
						if _u not in url_list:
							url_list.append(_u)
				except Exception as e:
					print('Baidu crawler is error: ',end='')
					print(e)
					continue
		webinfo = Webinfo()
		for url in url_list:
			webinfo.save_to_database(url)
			print("save %s to database success"% url )
		return len(url_list)

	
	def _rm_param(self,url):
		""" 去除链接中参数
		"""
		_u = urllib.parse.urlparse(url)
		new = _u.scheme + "://"+_u.netloc
		return new


	@async		
	def zoomeye_crawler(self,query,login=None,max_page = 1):
		""" 通过zoomeye获取数据
		:Parameter 
			- query: zoomeye 查询语句 ,query='app:phpcms country:cn'
			- login: 登录  login = ('username','password')
		e.x. 
		"""
		# 是否登录zoomeye通过api获取
		
		total = 0
		if login:
			# try:
			access_token = self._zoomeye_login(login[0],login[1])
			total = self._zoomeye_api(query,access_token,max_page)
			# except Exception as e:
			# 	print(e)
			# 	return 0
		else:
			# 爬取zoomeye页面
			total = self._zoomeye_crawl_page(query,max_page)
			
		return total

	def _zoomeye_crawl_page(self,query,max_page):
		page = 1
		url = 'https://www.zoomeye.org/search?q=%s&p=%s&t=web'%(query,page)
		headers = {
		'Host':"www.zoomeye.org",
		'User-Agent':"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
		'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		'Accept-Language':"en-US,en;q=0.5",
		'Accept-Encoding':"gzip, deflate",
		'Referer':url,
		'Cookie':"__jsluid=70d8f867aa7220a4225a179c46ec118e; csrftoken=V98Zi82dVIn62yKlIm9DMx4sbFuIm16r; sessionid=8xojqto0f38rx0ecejpleuy59iq2uwnh; __jsl_clearance=1492649384.488|0|l4cB8maFQhG2oSIS8C5%2BFiEYi6M%3D",
		'Connection':"keep-alive"
		}
		r = requests.get(url,headers=headers)
		tree = lxml.html.fromstring(r.text)
		result = tree.cssselect(".result.web li")
		print(len(result))
		return 0

	def _zoomeye_login(self,username,password):
		URI = "https://api.zoomeye.org/user/login"
		auth_data = {}
		auth_data["username"] = username
		auth_data["password"] = password
		auth_data = json.dumps(auth_data)
		r = requests.post(URI,data=auth_data)
		return r.json()['access_token']

	def _zoomeye_api(self,query,access_token,max_page):
		headers = {'Authorization':'JWT '+access_token}
		info = {}
		total = 0

		url = "https://api.zoomeye.org/web/search?query=%s&facets=os,app"%(query)
		print(type(max_page))
		max_page = int(max_page) + 1
		max_page += 1
		for p in range(1,max_page):
			page = "&page=%s" % str(p)
			url = url+page
			r = requests.get(url=url,headers=headers)
			try:
				datas = r.json().get("matches",None)
			except Exception as e:
				return "Can not found any data"
			for data in datas:
				info['db'] = data['db']
				info['geoinfo'] = data['geoinfo']
				info['ip'] = data['ip']
				info['language'] = data['language']
				info['server'] = data['server']
				info['site'] = data['site']
				info['title'] = data['title']
				info['webapp'] = data['webapp']
				info['headers'] = data['headers']
				info['system'] = data['system']

				self.mongodb.setitem(info)
				total += 1
				print("save %s success" % data['site'])
		print("_zoomeye_api total : {}".format(total))
		return total


def main():
	print('start')
	# crawl = Crawler()
	# querys = ['app:wordpress country:cn','app:phpcms country:cn','app:discuz country:cn']
	# login = ("username","password")
	# mongo = Mongodb()
	# for query in querys:
	# 	total = crawl.zoomeye_crawler(query=query,login=login,max_page=2)
	# 	print(total)
	
	# info = mongo.getitem()
	# pprint(info)
	
	# bquery = "inurl:*.cqu.edu.cn"
	# crawl.baidu_crawler(query=bquery,max_page=1)

if __name__ == '__main__':
	main()