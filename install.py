#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, configparser, shutil, subprocess

SERVICE_NAME = 'usbwatcher'
SERVICE_FILE = SERVICE_NAME + '.service'

ini = configparser.SafeConfigParser()
ini.read(SERVICE_FILE)
shutil.copy(SERVICE_NAME + '.py', ini.get('Service', 'ExecStart'))
shutil.copy(SERVICE_FILE, os.path.join('/usr/lib/systemd/system/', SERVICE_FILE))

subprocess.call(['systemctl', 'enable', SERVICE_FILE])
