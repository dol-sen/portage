#!/usr/bin/python -O


from __future__ import print_function


import portage
from portage import os
from portage.util import shlex_split, varexpand

## default clean command from make.globals
## PORT_LOGDIR_CLEAN = 'find "${PORT_LOGDIR}" -type f ! -name "summary.log*" -mtime +7 -delete'

class CleanLogs(object):

	short_desc = "Clean PORT_LOGDIR logs"

	def name():
		return "logs"
	name = staticmethod(name)


	def can_progressbar(self, func):
		return False


	def check(self, **kwargs):
		if kwargs:
			options = kwargs.get('options', None)
			if options:
				options['pretend'] = True
		return self.clean(**kwargs)


	def clean(self, **kwargs):
		"""Log directory cleaning function
		
		@param **kwargs: optional dictionary of values used in this function are:
			settings: portage settings instance: defaults to portage.settings
				"PORT_LOGDIR": directory to clean
				"PORT_LOGDIR_CLEAN": command for cleaning the logs.
			options: dict: 
				'NUM': int: number of days
				'pretend': boolean
				'eerror': defaults to None, optional output module to output errors.
				'einfo': defaults to None, optional output module to output info msgs.
		"""
		messages = []
		num_of_days = None
		if kwargs:
			# convuluted, I know, but portage.settings does not exist in
			# kwargs.get() when called from _emerge.main.clean_logs()
			settings = kwargs.get('settings', None)
			if not settings:
				settings = portage.settings
			options = kwargs.get('options', None)
			if options:
				num_of_days = options.get('NUM', None)
				pretend = options.get('pretend', False)
				eerror = options.get('eerror', None)
				einfo = options.get('einfo', None)

		clean_cmd = settings.get("PORT_LOGDIR_CLEAN")
		if clean_cmd:
			clean_cmd = shlex_split(clean_cmd)
			if '-mtime' in clean_cmd and num_of_days is not None:
				#print('changing the deafult number of days to:', num_of_days)
				if num_of_days == 0:
					i = clean_cmd.index('-mtime')
					clean_cmd.remove('-mtime')
					clean_cmd.pop(i)
				else:
					clean_cmd[clean_cmd.index('-mtime') +1] = \
						'+%s' % str(num_of_days)
			if pretend:
				if "-delete" in clean_cmd:
					#print('removing -delete')
					clean_cmd.remove("-delete")

		if not clean_cmd:
			return []
		rval = self._clean_logs(clean_cmd, settings)
		messages += self._convert_errors(rval, eerror, einfo)
		return messages


	@staticmethod
	def _clean_logs(clean_cmd, settings):
		logdir = settings.get("PORT_LOGDIR")
		if logdir is None or not os.path.isdir(logdir):
			return

		variables = {"PORT_LOGDIR" : logdir}
		cmd = [varexpand(x, mydict=variables) for x in clean_cmd]

		try:
			rval = portage.process.spawn(cmd, env=os.environ)
		except portage.exception.CommandNotFound:
			rval = 127
		return rval


	@staticmethod
	def _convert_errors(rval, eerror=None, einfo=None):
		msg = []
		if rval != os.EX_OK:
			msg.append("PORT_LOGDIR_CLEAN command returned %s"
				% ("%d" % rval if rval else "None"))
			msg.append("See the make.conf(5) man page for "
				"PORT_LOGDIR_CLEAN usage instructions.")
			if eerror:
				for m in msg:
					eerror(m)
		else:
			msg.append("PORT_LOGDIR_CLEAN command succeeded")
			if einfo:
				for m in msg:
					einfo(m)
		return msg
