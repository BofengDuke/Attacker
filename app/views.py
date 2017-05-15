#!/usr/bin/python
#-*- coding:utf-8 -*-

from flask import url_for,render_template,request,jsonify,redirect
from module.attack import single_host_attack,multi_host_attack
from module.mongodb import Mongodb
from module.crawler import Crawler
from app import app,socketio
from flask_socketio import emit,disconnect
import time

import sys
sys.path.append('..')
from config import PAGE_SIZE,USERNAME_Z,PASSWORD_Z



@app.route('/')
def index():
	title  = "Attacker"
	return render_template("index.html",**locals())

@app.route('/search',methods=['GET','POST'])
def search():
	start_time = time.time()
	action = request.args.get('action')
	datas = []
	title  = "搜索"
	max_page = 1
	curr_page = 1
	total = 0
	curr_path = request.url
	if action == 'query':
		params_all = request.args.get('params')
		page = request.args.get('page') 
		page =  int(page) if page != None else 1 
		curr_path = "&".join(curr_path.split('&')[0:2])
		# print("curr_page:",curr_path)
		try:
			params = parse_post_param(params_all)
		except Exception as e:
			error = "参数格式错误,无法处理"
			return render_template('error.html',error = error)
		mongodb = Mongodb()
		record = mongodb.query(query=params,page=page)
		curr_page = page
		total = record['total']
		datas = record['matches']
		max_page,_r = divmod(total,PAGE_SIZE)
		max_page = max_page + 1 if _r != 0 else max_page
	end_time = time.time()
	time_use = round((end_time - start_time) * 1000,3)
	return render_template('search.html',**locals(),async_mode=socketio.async_mode)

@app.route('/attack',methods=['GET','POST'])
def attack():
	if request.method == "POST":
		retdata = {}
		content = request.form.get('content')
		params = parse_post_param(content)
		module = params.get('use',None)
		if module == None:
			error = "Module can not be None!"
			retdata = {'error':error}
			return jsonify({'result':retdata})
		else:
			module = module.replace('/','.')

		if 'url' in params.keys():
			url = params.get('url')
			retdata = []
			ret = single_host_attack(module,url)
			retdata.append(ret)
			return jsonify({'result':retdata})

		if 'all' in params.keys():
			try:
				mongo = Mongodb()
			except Exception as e:
				return jsonify({'error':'数据库无法链接'})
			datas = mongo.getitem(num = -1)
			url_list = []
			for data in datas['matches']:
				url = data['webapp'][0]['url']
				url_list.append(url)
			retdata = multi_host_attack(module,url_list)
			return jsonify({'result':retdata})

		if 'webapp' in params.keys() or 'country' in params.keys():
			try:
				mongo = Mongodb()
			except Exception as e:
				return jsonify({'error':'数据库无法链接'})
			query = {}
			query['webapp'] = params.get('webapp','')
			query['country'] = params.get('country','')
			datas = mongo.query(query)['matches']
			url_list = []
			for item in datas:
				webapp = item['webapp']
				for app in webapp:
					url_list.append(app['url'])
			kwargs = {'module':module,'url_list':url_list}		
			# socketio.start_background_task(target=background_attack,**kwargs)
			# return jsonify({'result':'已经将攻击程序加入后台执行,,程序结束'})
			retdata = multi_host_attack(module,url_list)
			return jsonify({'result':retdata})
		return jsonify({'error':'格式错误'})

	title = "攻击"
	return render_template('attack.html',title=title,async_mode=socketio.async_mode)

def background_attack(module,url_list):
	""" 将多个攻击放入后台程序中执行,并将结果实时反馈回界面
	"""
	print('module ',end='')
	print(module)
	socketio.emit('attack_response',{'module':module},namespace='/attack')
	# for url in url_list:
	# 	info = single_host_attack(module,url)
	# 	print(info)
	# 	data = {'host':url,'info':info}
	# 	socketio.emit('attack_response',data,namespace="/attack")
	# disconnect()



def parse_post_param(param):
	""" 解析语句
		keys = ['use','url','all','app','country']
	"""
	items = param.split('||')
	params = {}
	for item in items:
		key,value = item.split()[0],item.split()[1]
		print(key,value)
		params[key] = value
	return params


@app.route('/managehost',methods=['GET'])
def managehost():
	action = request.args.get('action')
	if action == "removealldata":
		mongo  = Mongodb()
		try:
			dataNum = mongo.dropcollection()
			result = "删除成功！　共删除了　%s　条数据" % dataNum
			return jsonify({'result':result})
		except Exception as e:
			return jsonify({'error':'删除错误'})
	if action == "query":
		params_all = request.args.get('params')
		try:
			params = parse_post_param(params_all)
		except Exception as e:
			print("爬取的参数有错") 
			return jsonify({"error":"格式错误,请检查参数"})
		q_type = request.args.get('type')
		crawler = Crawler()
		if q_type == "baidu":
			try:
				query = params['query']
			except Exception:
				return jsonify({'error':'格式错误'})
			max_page = params.get('page','1')
			total = crawler.baidu_crawler(query=query,max_page=int(max_page))
			return jsonify({'result':'Baidu 总共爬取了 %s 条数据'%total})
		elif q_type == "zoomeye":
			_query = ''
			if 'app' in params.keys():
				_query += ' app:'+ params['app']
			if 'country' in params.keys():
				_query += ' country:'+params['country']
			if 'city' in params.keys():
				_query += ' city:'+params['city']
			max_page = params.get('page','1')
			if 'login' in params.keys():
				login = set(params['login'])
			else:
				login = (USERNAME_Z,PASSWORD_Z)
			total = crawler.zoomeye_crawler(query=_query,login=login,max_page=max_page)
			return jsonify({'result':'Zoomeye: {}'.format(total)})


		elif q_type == "iprange":
			return jsonify({'result':'总共爬取了 0 条数据'})


		print(queryData,q_type)
		return jsonify({'error':'00000'})

	title = '管理数据'
	mongo  = Mongodb()
	dataNum = mongo.getcount()
	return render_template('managehost.html',**locals(),async_mode=socketio.async_mode)


@app.route('/help')
def help():
	title = "帮助"
	return render_template('help.html',title=title)

# @app.errorhandler(500)
@app.errorhandler(404)
def not_found(error):
	return render_template('error.html',error="404",title="404")

# @app.route('/error')
# def error():
# 	title = "错误页面"


from app import views

