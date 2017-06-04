# 第三只眼 v1.0
基于空间搜索引擎的思路开发制作一个小型空间搜索引擎及攻击模型,可用于
安全研究人员快速分析出漏洞的影响范.项目还在持续更新完善.

本程序的python虚拟运行环境,可通过 requirements.txt 安装:
首先安装python3,以及 virtualenv 环境

```
# apt-get install python3
# python3 -m pip install virtualenv
```
    
接着在项目**Attacker/**目录中创建一个python的虚拟环境文件夹,并指定python3创建虚拟环境,
下面都是在**Attacker/**目录下进行

``` bash
# virtualenv -p /usr/bin/python3 venv3
```

启动虚拟环境，并安装项目依赖（在 **Attacker/** 下有requirements.txt）

```bash
# source venv3/bin/activate
# python3 -m pip install -r requirements.txt
```


项目还依赖 Mongodb 的环境,安装方法请自己查询。 [Mongodb官网](https://www.mongodb.com/)

启动运行环境后就可以运行程序
程序运行:
```
# service mongodb start  或者 ./start_service.sh
# python3 run.py
```



