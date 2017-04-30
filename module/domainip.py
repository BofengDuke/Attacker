#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: 查询IP对应的域名
'''
import lxml.html
import requests

def get_domain(ip):
	''' 获取查询页面
	'''
	url = 'http://dns.aizhan.com/%s/' % ip
	r = requests.get(url)
	r.encoding = r.apparent_encoding
	tree = lxml.html.fromstring(r.text)
	page_num = _get_max_page_num(r.text)
	domains = []
	for page in range(1,page_num+1):
		dnslinks = tree.cssselect('.dns-links')
		if len(dnslinks) != 0:
			for dns in dnslinks:
				d = lxml.html.tostring(dns,method='text',encoding='unicode').strip()
				domains.append(d)
	return domains


def _get_max_page_num(html):
	tree = lxml.html.fromstring(html)
	getmear = tree.cssselect('#getmear a')
	return len(getmear)+1
	