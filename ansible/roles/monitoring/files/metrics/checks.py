import psutil
import json
import time

#Change the path to make the check in the host server
psutil.PROCFS_PATH = '/proc_host'

def cpucheck():
	cpuusage = json.dumps({'cpu_percent': psutil.cpu_percent()})
	return cpuusage

def memorycheck():
	memoryusage = json.dumps({'memory_percent': psutil.virtual_memory().percent,
							'cache_percent': psutil.virtual_memory().cached / psutil.virtual_memory().total * 100,
							'swap_percent': psutil.swap_memory().percent})
	return memoryusage

def diskcheck():
	diskusage = json.dumps({'disk_percent': psutil.disk_usage('/').percent})
	return diskusage

def netcheck():
	netusage = json.dumps({'net_fds': psutil.net_connections()})
	return netusage

def servicheck():
	serviceusage = json.dumps({p.pid: p.info for p in psutil.process_iter(attrs=['name', 'username'])})
	return serviceusage
	