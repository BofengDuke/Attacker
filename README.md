# 第三只眼 v1.0


本程序的python虚拟运行环境,可通过 requirements.txt 安装:
首先安装python3,以及 virtualenv 环境

```
# apt-get install python3
# python3 -m pip install virtualenv
```
    
接着创建一个python的虚拟环境文件夹,并指定python3创建虚拟环境,
然后启动环境
```
# virtualenv -p /usr/bin/python3 venv3
# source venv3/bin/activate
```

启动运行环境后就可以运行程序
程序运行:
```
# service mongodb start  或者 ./start_service.sh
# python3 run.py
```



