#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: web指纹识别 
基于网站页面 title,head,body 匹配特征

1. 基于web网站独有的favicon.ico的md5 比对网站类型；

2. 基于规则识别web站特征去识别；

3. 基于爬虫爬出来的网站目录比对web信息。
'''
import sys
import requests,urllib
import re,json
import lxml.html
import hashlib

sys.path.append('/rule')
from rule import page_rule


class webfingerprint():
	"""获取web信息

	"""
	def __init__(self, url):
		"""
		:Parameter
			- url: http://demo.org
		"""
		self.url = url
		r = requests.get(self.url)
		r.encoding = r.apparent_encoding
		self.tree = lxml.html.fromstring(r.text)
		self.html = r.text
		self.response = r
		self.web_info = {}

	def from_robots(self):
		uri = self.url+'/robots.txt'
		r = requests.get(uri)
		if r.status_code != 200:
			return None

		# cms = {'phpcms':'phpcms'}
		pattern = r'phpcms'
		m = re.search(pattern,r.text,re.I)
		if m is not None:
			return pattern
		else:
			return None

	""" _scan_title,_scan_head,_scan_body,_scan_page 
	都是通过匹配
	"""
	def _scan_title(self):
		finger_title = page_rule.title
		title = self.get_title()
		for key in finger_title.keys():
			m = re.search(key,title,re.I)
			if m != None:
				return finger_title[m]
		return None

	def _scan_head(self):
		finger_head = page_rule.head
		try:
			head = self.tree.cssselect('head')[0]
			head = lxml.html.tostring(head,method='html',encoding='unicode').strip()
		except Exception as e:
			return None
		for key in finger_head.keys():
			if '&' in key:
				keys = key.split('&')
				if re.search(keys[0],head,re.I) and re.search(keys[1],head,re.I):
					return finger_head[key]
			else:
				if re.search(key,head,re.I):
					return finger_head[key]
		return None

	def _scan_body(self):
		finger_body = page_rule.body
		try:
			body = self.tree.cssselect('body')[0]
			body = lxml.html.tostring(body,method='html',encoding='unicode').strip()
		except Exception as e:
			return None
		for key in finger_body.keys():
			if '&' in key:
				keys = key.split('&')
				if re.search(keys[0],body,re.I) and re.search(keys[1],body,re.I):
					return finger_body[key]
			else:
				if re.search(key,body,re.I):
					return finger_body[key]
		return None

	def _scan_page(self):
		with open("rule/whatweb.json") as fp:
			rules_dict = json.load(fp)
			for cms in rules_dict.keys():
				rules_list = rules_dict[cms]
				for rule in rules_list:
					try:
						if rule['url'] != '/':
							url = self.url + rule['url']
							r = requests.get(url,timeout=10)
							r.encoding = r.apparent_encoding
							r.close()
						else:
							r = self.response
						if "md5" in rule and hashlib.md5(r.content).hexdigest() == rule['md5']:
							return cms
						elif "text" in rule:
							if isinstance(rule['text'],list):
								for itext in rule['text']:
									if itext in r.text:
										return cms
							elif rule['text'] in r.text:
								return cms
						elif "regexp" in rule:
							if isinstance(rule['regexp'],list):
								for reg in rule['regexp']:
									if re.search(reg,r.text):
										return cms
							elif re.search(rule['regexp'],r.text):
								return cms
					except Exception as e:
						print("[Error]: web_fingerprint.py  _scan_page(): ",end='')
						print(e)
						pass
			return None

	def get_header(self):
		info = self.response.headers
		header = []
		for key,value in info.items():
			header.append(key+": "+value)
			# print(key+": "+value)
		return header

	def _get_server_from_header(self):
		return self.response.headers.get('Server',None)

	def _get_language_from_header(self):
		return self.response.headers.get('X-Powered-By',None)

	def get_webapp(self):
		webapp = {}
		if self._scan_title():
			webapp['name'] = self._scan_title()
		elif self._scan_head():
			webapp['name'] = self._scan_head()
		elif self._scan_body():
			webapp['name'] = self._scan_body()
		elif self._scan_page():
			webapp['name'] = self._scan_page()
		else:
			webapp['name'] = ""

		webapp['url'] = self.url
		webapp['version'] = ""
		return webapp

	def get_title(self):
		title = ""
		try:
			title = self.tree.cssselect('title')[0]
			title = lxml.html.tostring(title,method='html',encoding='unicode').strip()
		except Exception:
			title = ""
		return title

	def get_language(self):
		return self._get_language_from_header()

	def get_server(self):
		server = {}
		server['name'] = self._get_server_from_header()
		server['version'] = ""
		return server


def main():
	url = 'http://cqyixiao.com'
	# url = 'http://news.cqu.edu.cn'
	F = webfingerprint(url)
	f = F.get_webapp()
	h = F.get_header()
	s = F.get_server_from_header()
	l = F.get_language_from_header()
	#
	print('-----webapp-------')
	print(f)
	print('------header-------')
	print(h)
	print('-------server------')
	print(s)
	print('------language-------')
	print(l)
	# F.get_header()


if __name__ == '__main__':
	main()

		
		