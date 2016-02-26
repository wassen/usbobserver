#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time, sys, subprocess, configparser, string, logging, tempfile
from mediafire import (MediaFireApi, MediaFireUploader)
import subprocess as sp

#自作モジュール
#from createdaemon import create_daemon

def create_daemon(task, **kwargs):
	#wikipediaのforkを参照
	#https://ja.wikipedia.org/wiki/Fork

	logFileName = kwargs['logFileName'] if 'logFileName' in kwargs else '/var/log/createdaemon'

	logging.basicConfig(
		filename=logFileName,
		level=logging.DEBUG,
		format="%(asctime)s %(levelname)s %(message)s"
	)
	
	if os.getuid() == 0:
		print('root user')
	else:
		print("non-root user")
		# sys.exit()

	try:
		pid = os.fork()
	except OSError as err:
		logging.warning('Unable to fork. Error: {0} ({1})'.format(err.errno, err.strerror))
		sys.exit(1)

	if pid > 0:
		logging.debug('PID: %d' % pid)
		with open('/var/run/usbwatcher.pid','w') as f:
			f.write(str(pid) + '\n')
		sys.exit()
	else:
		while True:
			task()

#change initfile's key to Default andsoon (change in context)

INI_FILE = '/mnt/usb1/.MFUp_config'#/etc/

#evernote編集しましょう

def is_mounted_device(device):
	df = sp.Popen(['df'], stdout = sp.PIPE)
	grep = sp.Popen(['grep', device], stdin = df.stdout, stdout = sp.PIPE)
	return True if list(grep.stdout) else False

mountedList = {}
	
def watch_usb():
	logFileName = '/var/log/usbwatcher'
	logging.basicConfig(
		filename=logFileName,
		level=logging.DEBUG,
		format="%(asctime)s %(levelname)s %(message)s"
	)
	
	for alphabet in string.ascii_lowercase:
		device = '/dev/sd' + alphabet
		if os.path.exists(device) and not is_mounted_device(device):
			logging.info('Found an unmounted device: {}'.format(device))
			mountpoint = tempfile.mkdtemp(dir='/mnt/')
			if subprocess.call(['mount', device + str(1), mountpoint]):
				logging.warning('Unable to mount.')
			else: 
				logging.info('Mount success.')
				mountedList[device] = mountpoint
		elif not os.path.exists(device) and device in mountedList:
			logging.info('device:{} was ejected'.format(device))
			mountedpoint = mountedList.pop(device)
			if subprocess.call(['umount', mountedpoint]):
				logging.warning('Unable to unmount')
			else: 
				logging.info('Unmount success')
				os.rmdir(mountedpoint)
	time.sleep(5)

if __name__ == '__main__':
	create_daemon(watch_usb)
