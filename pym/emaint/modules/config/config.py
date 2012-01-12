#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import portage
from portage import os
from portage.const import PRIVATE_PATH
from portage.checksum import perform_md5


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

	def check(self,  **kwargs):
		onProgress = kwargs.get('onProgress', None)
		configs = self.load_configlist()
		messages = []
		chksums = []
		maxval = len(configs)
		if onProgress:
			onProgress(maxval, 0)
			i = 0
		keys = sorted(configs)
		for config in keys:
			if os.path.exists(config):
				md5sumactual = perform_md5(config)
				if md5sumactual != configs[config]:
					chksums.append("  %s" % config)
			else:
				messages.append("  %s" % config)
			if onProgress:
				onProgress(maxval, i+1)
				i += 1
		return self._format_output(messages, chksums)

	def fix(self, **kwargs):
		onProgress = kwargs.get('onProgress', None)
		configs = self.load_configlist()
		messages = []
		chksums = []
		maxval = len(configs)
		if onProgress:
			onProgress(maxval, 0)
			i = 0
		keys = sorted(configs)
		for config in keys:
			if os.path.exists(config):
				md5sumactual = perform_md5(config)
				if md5sumactual != configs[config]:
					chksums.append("  %s" % config)
					chksum = configs.pop(config)
			else:
					chksum = configs.pop(config)
					messages.append("  %s" % config)
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
		return self._format_output(messages, chksums, True)

	def _format_output(self, messages=[], chksums=[], cleaned=False):
		output = []
		if messages:
			output.append('Not Installed:')
			output += messages
			tot = '------------------------------------\n  Total %i Not installed'
			if cleaned:
				tot += ' ...Cleaned'
			output.append(tot  % len(messages))
		if chksums:
			output.append('\nChecksums did not match:')
			output += chksums
			tot = '------------------------------------\n  Total %i Checksums did not match'
			if cleaned:
				tot += ' ...Cleaned'
			output.append(tot % len(chksums))
		return output
