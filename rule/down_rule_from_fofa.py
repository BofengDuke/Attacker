#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: fofa.so 下载规则 
'''

import lxml.html
import base64
import urllib,requests



url = 'https://fofa.so/library'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.0.1471.914 Safari/537.36'}


def parse_base64(url):
	if url == "/library":
		return url
	url = url.split('=')[1]
	url = urllib.parse.unquote(url)
	url = base64.b64decode(url).decode()
	return url

def get_rules(html):
	tree = lxml.html.fromstring(html)
	panel = tree.cssselect('.panel.panel-default')
	rules = {}
	for p in panel:
		type_name = p.cssselect('.panel-heading label')[0]
		type_name = lxml.html.tostring(type_name,method="text",encoding="utf-8").decode('utf-8')
		type_name = type_name.strip()
		rules_list = p.cssselect('.panel-body a')
		tmp = {}
		for a in rules_list:
			name = lxml.html.tostring(a,method="text",encoding="utf-8").decode('utf-8').strip()
			rule = a.get('href')
			rule = parse_base64(rule).strip()
			tmp[name] = rule
		rules[type_name] = tmp
	return rules

def save_to_file(rules):
	with open("test.txt",'w') as fp:
		for item in rules:
			rule_list = rules[item]
			for name,rule in rule_list.items():
				if rule == '/libary':
					print('Not found')
				else:
					s = item+" "+name+" "+rule+"\n"
					fp.write(s)

def main():
	r = requests.get(url,headers=headers)
	rules = get_rules(r.text)
	save_to_file(rules)
	


if __name__ == '__main__':
	main()
