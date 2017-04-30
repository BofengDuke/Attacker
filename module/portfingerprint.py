#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: 使用nmap 进行扫描
'''

# class PortSscanner():
# 	"""docstring for PortSscanner"""
# 	def __init__(self, ):
# 		self.arg = arg


import nmap,socket
import pprint
import re

# -sV 服务探测
# -O 系统探测
# -p 端口探测
# -F 快速检测

def port_scan(hosts,ports=None,arguments='-sV -F -O'):
	nm = nmap.PortScanner()
	results = nm.scan(hosts=hosts,ports=ports,arguments=arguments)
	info = {}
	curr_host = nm[nm.all_hosts()[0]]
	info['ipv4'] = curr_host['addresses']['ipv4']
	info['donmain'] = curr_host['hostnames'][0]['name']
	info['os'] = 'None'
	os = str(curr_host['osmatch'])
	if re.search('linux',os,re.I):
		info['os'] = 'Linux'
	if re.search('windows',os,re.I):
		info['os'] = 'Windows'
	info['status'] = curr_host['status']['state']
	info['port'] = []
	if curr_host['tcp'] != None:
		for port,value in curr_host['tcp'].items():
			if value['state'] != 'closed':
				p = {port:{'name':value['name'],'product':value['product'],'state':value['state']}}
				info['port'].append(p)

	return info



if __name__ == '__main__':
	hosts = 'duebf.org'
	# r = port_scan(hosts=hosts)
	# pprint.pprint(r)

