#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import portage
from portage import os



class MoveHandler(object):

	def __init__(self, tree):
		self._tree = tree
		self._portdir = tree.settings["PORTDIR"]
		self._update_keys = ["DEPEND", "RDEPEND", "PDEPEND", "PROVIDE"]

	def _grab_global_updates(self, portdir):
		from portage.update import grab_updates, parse_updates
		updpath = os.path.join(portdir, "profiles", "updates")
		try:
			rawupdates = grab_updates(updpath)
		except portage.exception.DirectoryNotFound:
			rawupdates = []
		upd_commands = []
		errors = []
		for mykey, mystat, mycontent in rawupdates:
			commands, errors = parse_updates(mycontent)
			upd_commands.extend(commands)
			errors.extend(errors)
		return upd_commands, errors

	def check(self, onProgress=None):
		updates, errors = self._grab_global_updates(self._portdir)
		# Matching packages and moving them is relatively fast, so the
		# progress bar is updated in indeterminate mode.
		match = self._tree.dbapi.match
		aux_get = self._tree.dbapi.aux_get
		if onProgress:
			onProgress(0, 0)
		for i, update_cmd in enumerate(updates):
			if update_cmd[0] == "move":
				origcp, newcp = update_cmd[1:]
				for cpv in match(origcp):
					errors.append("'%s' moved to '%s'" % (cpv, newcp))
			elif update_cmd[0] == "slotmove":
				pkg, origslot, newslot = update_cmd[1:]
				for cpv in match(pkg):
					slot = aux_get(cpv, ["SLOT"])[0]
					if slot == origslot:
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
		update_keys = self._update_keys
		from portage.update import update_dbentries
		if onProgress:
			onProgress(maxval, 0)
		for i, cpv in enumerate(cpv_all):
			metadata = dict(zip(update_keys, aux_get(cpv, update_keys)))
			metadata_updates = update_dbentries(updates, metadata)
			if metadata_updates:
				errors.append("'%s' has outdated metadata" % cpv)
			if onProgress:
				onProgress(maxval, i+1)
		return errors

	def fix(self, onProgress=None):
		updates, errors = self._grab_global_updates(self._portdir)
		# Matching packages and moving them is relatively fast, so the
		# progress bar is updated in indeterminate mode.
		move = self._tree.dbapi.move_ent
		slotmove = self._tree.dbapi.move_slot_ent
		if onProgress:
			onProgress(0, 0)
		for i, update_cmd in enumerate(updates):
			if update_cmd[0] == "move":
				move(update_cmd)
			elif update_cmd[0] == "slotmove":
				slotmove(update_cmd)
			if onProgress:
				onProgress(0, 0)

		# Searching for updates in all the metadata is relatively slow, so this
		# is where the progress bar comes out of indeterminate mode.
		self._tree.dbapi.update_ents(updates, onProgress=onProgress)
		return errors

class MoveInstalled(MoveHandler):

	short_desc = "Perform package move updates for installed packages"

	def name():
		return "moveinst"
	name = staticmethod(name)
	def __init__(self):
		myroot = portage.settings["ROOT"]
		MoveHandler.__init__(self, portage.db[myroot]["vartree"])

class MoveBinary(MoveHandler):

	short_desc = "Perform package move updates for binary packages"

	def name():
		return "movebin"
	name = staticmethod(name)
	def __init__(self):
		myroot = portage.settings["ROOT"]
		MoveHandler.__init__(self, portage.db[myroot]["bintree"])
