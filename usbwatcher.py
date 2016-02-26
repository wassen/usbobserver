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

	#try except for config.read
def MFUp():
	if os.path.exists(INI_FILE):
		config = configparser.SafeConfigParser()
		config.read(INI_FILE)
		upDir = config.get('MFUp','upDir')
		#nesesally '\' end of upDir
		cancel = config.get('MFUp','cancel')
	else:
		print ("Can't find setting file(%s)" % INI_FILE)#check this
		if subprocess.call(['umount','/dev/sda1']):
			print ('Unable to unmount.')
		else:
			print('Umount success')
		return

	if int(cancel) > 0:
		print('Upload aborted')
		return

	subprocess.call(['cp','-r','/mnt/usb1/' + upDir,'/var/tmp/']) #doesnt check the duplication
	print ('Success to copy')

	if subprocess.call(['umount','/dev/sda1']):
		print ('Unable to unmount.')
	else:
		print('Umount success.')

	api = MediaFireApi()
	uploader = MediaFireUploader(api)

	session = api.user_get_session_token(
		email = 'dmcvpedf1@yahoo.co.jp',
		password = 'ipitracyMED9',
		app_id = '48204')
	api.session = session
	print ('Made session.')

	uplist = os.listdir('/var/tmp/' + upDir)
	#Assume that file only #Recursively

	for upfile in uplist:
		print('Starting upload of '+upfile)
		fd = open('/var/tmp/' + upDir + upfile, 'rb')
		print ('/var/tmp/' + upDir + upfile)
		upload_result = uploader.upload(fd, upfile)
		api.file_update(upload_result.quickkey,privacy='private')
		#change updir of Mediafire (now only root)
		# change /var/tmp to /tmp
		# erase Unnecessarry file

if __name__ == '__main__':
	#create_daemon(watch_usb)
	while True:
		watch_usb()
