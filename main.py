#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time, sys, subprocess,configparser
from mediafire import (MediaFireApi, MediaFireUploader)
#import usb
#checkDev(1423,25464)
#change initfile's key to Default andsoon (change in context)

INI_FILE = '/mnt/usb1/.MFUp_config'

#evernote編集しましょう
def createDaemon():
#refer wikipedia fork
	try:
		pid = os.fork()
	
		if pid > 0:
			print ('PID: %d' % pid)
			f = open('/var/run/usbobserver.pid','w')
			f.write(str(pid) + '\n')
			f.close()
			sys.exit()
			
	except OSError as error:
		print ('Unable to fork. Error: %d (%s)' % (error.errno, error.strerror))
		sys.exit(1)
	
	doTask()

def doTask():
	log_file = open('/tmp/tarefa.log', 'w')

	usbInsFlag = False
	while True:
		if os.path.exists('/dev/sda') and not usbInsFlag:
			print('USB memory found')
			if subprocess.call(['mount','/dev/sda1','/mnt/usb1']):
				print('Unable to mount.')
			else:
				print('Mount success.')
			usbInsFlag = True
			MFUp();
			
		elif not os.path.exists('/dev/sda') and usbInsFlag:
			print('USB memory was ejected')
			usbInsFlag = False
		else:
			time.sleep(5)
	log_file.close()
	
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
	if os.getuid() == 0:
		print ("root!")
	else:
		print ('non-root user!')
		sys.exit()
	createDaemon()
