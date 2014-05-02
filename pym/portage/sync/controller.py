# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

from __future__ import print_function


import sys
import logging
import pwd

import portage
from portage import os
from portage.emaint.progress import ProgressBar
#from portage.emaint.defaults import DEFAULT_OPTIONS
#from portage.util._argparse import ArgumentParser
from portage.util import writemsg_level
from portage.output import create_color_func
good = create_color_func("GOOD")
bad = create_color_func("BAD")
warn = create_color_func("WARN")
from portage.package.ebuild.doebuild import _check_temp_dir
from portage.metadata import action_metadata


class TaskHandler(object):
	"""Handles the running of the tasks it is given
	"""

	def __init__(self, show_progress_bar=True, verbose=True, callback=None):
		self.show_progress_bar = show_progress_bar
		self.verbose = verbose
		self.callback = callback
		self.isatty = os.environ.get('TERM') != 'dumb' and sys.stdout.isatty()
		self.progress_bar = ProgressBar(self.isatty, title="Portage-Sync", max_desc_length=27)


	def run_tasks(self, tasks, func, status=None, verbose=True, options=None):
		"""Runs the module tasks"""
		if tasks is None or func is None:
			return
		for task in tasks:
			inst = task()
			show_progress = self.show_progress_bar and self.isatty
			# check if the function is capable of progressbar
			# and possibly override it off
			if show_progress and hasattr(inst, 'can_progressbar'):
				show_progress = inst.can_progressbar(func)
			if show_progress:
				self.progress_bar.reset()
				self.progress_bar.set_label(func + " " + inst.name())
				onProgress = self.progress_bar.start()
			else:
				onProgress = None
			kwargs = {
				'onProgress': onProgress,
				# pass in a copy of the options so a module can not pollute or change
				# them for other tasks if there is more to do.
				'options': options.copy()
				}
			result = getattr(inst, func)(**kwargs)
			if show_progress:
				# make sure the final progress is displayed
				self.progress_bar.display()
				print()
				self.progress_bar.stop()
			if self.callback:
				self.callback(result)


def print_results(results):
	if results:
		print()
		print("\n".join(results))
		print("\n")


class SyncManager(object):
	'''Main sync control module'''

	def __init__(self, settings, logger):
		self.logger = logger
		# Similar to emerge, sync needs a default umask so that created
		# files have sane permissions.
		os.umask(0o22)

		self.module_controller = portage.sync.module_controller
		self.module_names = self.module_controller.module_names[:]


	def get_module_descriptions(self, mod):
		desc = self.module_controller.get_func_descriptions(mod)
		if desc:
			return desc
		return []


	def sync(self, emerge_config=None, repo=None, callback=None):
		self.emerge_config = emerge_config
		self.callback = callback or self._sync_callback
		self.repo = repo
		self.exitcode = 1
		if repo.sync_type in self.module_names[1:]:
			tasks = [self.module_controller.get_class(repo.sync_type)]
		else:
			portage.util.writemsg(
				"\nERROR: Sync module '%s' is not an installed/known type'\n\n"
				% (repo.sync_type), noiselevel=-1)
			return self.exitcode

		rval = self.pre_sync(repo)
		if rval != os.EX_OK:
			return rval

		# need to pass the kwargs dict to the modules
		# so they are available if needed.
		task_opts = {
			'emerge_config': emerge_config,
			'logger': self.logger,
			'portdb': self.trees[self.settings['EROOT']]['porttree'].dbapi,
			'repo': repo,
			'settings': self.settings,
			'spawn_kwargs': self.spawn_kwargs,
			'usersync_uid': self.usersync_uid,
			'xterm_titles': self.xterm_titles,
			}
		func = 'sync'
		status = None
		taskmaster = TaskHandler(callback=self.do_callback)
		taskmaster.run_tasks(tasks, func, status, options=task_opts)

		self.perform_post_sync_hook(repo.sync_uri)

		return self.exitcode


	def do_callback(self, result):
		#print("result:", result, "callback()", self.callback)
		exitcode, updatecache_flg = result
		if self.callback:
			self.callback(exitcode, updatecache_flg)
		return


	def perform_post_sync_hook(self, dosyncuri):
		postsync = os.path.join(self.settings["PORTAGE_CONFIGROOT"],
			portage.USER_CONFIG_PATH, "bin", "post_sync")
		if os.access(postsync, os.X_OK):
			retval = portage.process.spawn([postsync, dosyncuri],
				env=self.settings.environ())
			if retval != os.EX_OK:
				writemsg_level(" %s spawn failed of %s\n" % (bad("*"),
					postsync,), level=logging.ERROR, noiselevel=-1)
		return retval


	def pre_sync(self, repo):
		self.settings, self.trees, self.mtimedb = self.emerge_config
		self.xterm_titles = "notitles" not in self.settings.features
		msg = ">>> Synchronization of repository '%s' located in '%s'..." \
			% (repo.name, repo.location)
		self.logger(self.xterm_titles, msg)
		writemsg_level(msg + "\n")
		try:
			st = os.stat(repo.location)
		except OSError:
			st = None
		if st is None:
			print(">>> '%s' not found, creating it." % repo.location)
			portage.util.ensure_dirs(repo.location, mode=0o755)
			st = os.stat(repo.location)

		self.usersync_uid = None
		spawn_kwargs = {}
		spawn_kwargs["env"] = self.settings.environ()
		if 'usersync' in self.settings.features and \
			portage.data.secpass >= 2 and \
			(st.st_uid != os.getuid() and st.st_mode & 0o700 or \
			st.st_gid != os.getgid() and st.st_mode & 0o070):
			try:
				homedir = pwd.getpwuid(st.st_uid).pw_dir
			except KeyError:
				pass
			else:
				# Drop privileges when syncing, in order to match
				# existing uid/gid settings.
				self.usersync_uid = st.st_uid
				spawn_kwargs["uid"]    = st.st_uid
				spawn_kwargs["gid"]    = st.st_gid
				spawn_kwargs["groups"] = [st.st_gid]
				spawn_kwargs["env"]["HOME"] = homedir
				umask = 0o002
				if not st.st_mode & 0o020:
					umask = umask | 0o020
				spawn_kwargs["umask"] = umask
		self.spawn_kwargs = spawn_kwargs

		if self.usersync_uid is not None:
			# PORTAGE_TMPDIR is used below, so validate it and
			# bail out if necessary.
			rval = _check_temp_dir(self.settings)
			if rval != os.EX_OK:
				return rval

		os.umask(0o022)
		return os.EX_OK


	def _sync_callback(self, exitcode, updatecache_flg):
		if updatecache_flg and "metadata-transfer" not in self.settings.features:
			updatecache_flg = False

		if updatecache_flg and \
			os.path.exists(os.path.join(self.repo.location, 'metadata', 'cache')):

			# Only update cache for repo.location since that's
			# the only one that's been synced here.
			action_metadata(self.settings, self.portdb, self.emerge_config.opts,
				porttrees=[self.repo.location])

