#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import portage
from portage import os



class MoveHandler(object):

	def __init__(self, tree, porttree):
		self._tree = tree
		self._portdb = porttree.dbapi
		self._update_keys = ["DEPEND", "RDEPEND", "PDEPEND", "PROVIDE"]
		self._master_repo = \
			self._portdb.getRepositoryName(self._portdb.porttree_root)

	def _grab_global_updates(self):
		from portage.update import grab_updates, parse_updates
		retupdates = {}
		errors = []

		for repo_name in self._portdb.getRepositories():
			repo = self._portdb.getRepositoryPath(repo_name)
			updpath = os.path.join(repo, "profiles", "updates")
			if not os.path.isdir(updpath):
				continue

			try:
				rawupdates = grab_updates(updpath)
			except portage.exception.DirectoryNotFound:
				rawupdates = []
			upd_commands = []
			for mykey, mystat, mycontent in rawupdates:
				commands, errors = parse_updates(mycontent)
				upd_commands.extend(commands)
				errors.extend(errors)
			retupdates[repo_name] = upd_commands

		if self._master_repo in retupdates:
			retupdates['DEFAULT'] = retupdates[self._master_repo]

		return retupdates, errors

	def check(self, onProgress=None):
		allupdates, errors = self._grab_global_updates()
		# Matching packages and moving them is relatively fast, so the
		# progress bar is updated in indeterminate mode.
		match = self._tree.dbapi.match
		aux_get = self._tree.dbapi.aux_get
		if onProgress:
			onProgress(0, 0)
		for repo, updates in allupdates.items():
			if repo == 'DEFAULT':
				continue
			if not updates:
				continue

			def repo_match(repository):
				return repository == repo or \
					(repo == self._master_repo and \
					repository not in allupdates)

			for i, update_cmd in enumerate(updates):
				if update_cmd[0] == "move":
					origcp, newcp = update_cmd[1:]
					for cpv in match(origcp):
						if repo_match(aux_get(cpv, ["repository"])[0]):
							errors.append("'%s' moved to '%s'" % (cpv, newcp))
				elif update_cmd[0] == "slotmove":
					pkg, origslot, newslot = update_cmd[1:]
					for cpv in match(pkg):
						slot, prepo = aux_get(cpv, ["SLOT", "repository"])
						if slot == origslot and repo_match(prepo):
							errors.append("'%s' slot moved from '%s' to '%s'" % \
								(cpv, origslot, newslot))
				if onProgress:
					onProgress(0, 0)

		# Searching for updates in all the metadata is relatively slow, so this
		# is where the progress bar comes out of indeterminate mode.
		cpv_all = self._tree.dbapi.cpv_all()
		cpv_all.sort()
		maxval = len(cpv_all)
		aux_update = self._tree.dbapi.aux_update
		meta_keys = self._update_keys + ['repository']
		from portage.update import update_dbentries
		if onProgress:
			onProgress(maxval, 0)
		for i, cpv in enumerate(cpv_all):
			metadata = dict(zip(meta_keys, aux_get(cpv, meta_keys)))
			repository = metadata.pop('repository')
			try:
				updates = allupdates[repository]
			except KeyError:
				try:
					updates = allupdates['DEFAULT']
				except KeyError:
					continue
			if not updates:
				continue
			metadata_updates = update_dbentries(updates, metadata)
			if metadata_updates:
				errors.append("'%s' has outdated metadata" % cpv)
			if onProgress:
				onProgress(maxval, i+1)
		return errors

	def fix(self, onProgress=None):
		allupdates, errors = self._grab_global_updates()
		# Matching packages and moving them is relatively fast, so the
		# progress bar is updated in indeterminate mode.
		move = self._tree.dbapi.move_ent
		slotmove = self._tree.dbapi.move_slot_ent
		if onProgress:
			onProgress(0, 0)
		for repo, updates in allupdates.items():
			if repo == 'DEFAULT':
				continue
			if not updates:
				continue

			def repo_match(repository):
				return repository == repo or \
					(repo == self._master_repo and \
					repository not in allupdates)

			for i, update_cmd in enumerate(updates):
				if update_cmd[0] == "move":
					move(update_cmd, repo_match=repo_match)
				elif update_cmd[0] == "slotmove":
					slotmove(update_cmd, repo_match=repo_match)
				if onProgress:
					onProgress(0, 0)

		# Searching for updates in all the metadata is relatively slow, so this
		# is where the progress bar comes out of indeterminate mode.
		self._tree.dbapi.update_ents(allupdates, onProgress=onProgress)
		return errors

class MoveInstalled(MoveHandler):

	short_desc = "Perform package move updates for installed packages"

	def name():
		return "moveinst"
	name = staticmethod(name)
	def __init__(self):
		eroot = portage.settings['EROOT']
		MoveHandler.__init__(self, portage.db[eroot]["vartree"], portage.db[eroot]["porttree"])

class MoveBinary(MoveHandler):

	short_desc = "Perform package move updates for binary packages"

	def name():
		return "movebin"
	name = staticmethod(name)
	def __init__(self):
		eroot = portage.settings['EROOT']
		MoveHandler.__init__(self, portage.db[eroot]["bintree"], portage.db[eroot]['porttree'])
