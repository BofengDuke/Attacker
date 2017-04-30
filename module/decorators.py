from threading import Thread

def async(f):
	def wrapper(*args,**kwargs):
		thread = Thread(target = f,args = args,kwargs=kwargs)
		thread.start()
	return wrapper