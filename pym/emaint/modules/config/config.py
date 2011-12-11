#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import portage
from portage import os
from portage.const import PRIVATE_PATH


class CleanConfig(object):

	short_desc = "Discard any no longer installed configs from emerge's tracker list"
	target = os.path.join(portage.settings["EROOT"], PRIVATE_PATH, 'config')

	def name():
		return "cleanconfig"
	name = staticmethod(name)

	def load_configlist(self):
		
		configs = {}
		with open(self.target, 'r') as configfile:
			lines = configfile.readlines()
		for line in lines:
			ls = line.split()
			configs[ls[0]] = ls[1]
		return configs

	def check(self, onProgress=None):
		configs = self.load_configlist()
		messages = []
		maxval = len(configs)
		if onProgress:
			onProgress(maxval, 0)
			i = 0
		keys = sorted(configs)
		for config in keys:
			if not os.path.exists(config):
				messages.append("Not installed: %s %s" % (config, configs[config]))
			if onProgress:
				onProgress(maxval, i+1)
				i += 1
		return messages

	def fix(self, onProgress=None):
		configs = self.load_configlist()
		messages = []
		maxval = len(configs)
		if onProgress:
			onProgress(maxval, 0)
			i = 0
		keys = sorted(configs)
		for config in keys:
				if not os.path.exists(config):
					chksum = configs.pop(config)
					messages.append("Cleaned: %s %s" % (config, chksum))
				if onProgress:
					onProgress(maxval, i+1)
					i += 1
		lines = []
		keys = sorted(configs)
		for key in keys:
			line = ' '.join([key, configs[key]])
			lines.append(line)
		lines.append('')
		with open(self.target, 'w') as configfile:
			configfile.write('\n'.join(lines))
		return messages
