#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import portage
from portage import os



class BinhostHandler(object):

	short_desc = "Generate a metadata index for binary packages"

	def name():
		return "binhost"
	name = staticmethod(name)

	def __init__(self):
		myroot = portage.settings["ROOT"]
		self._bintree = portage.db[myroot]["bintree"]
		self._bintree.populate()
		self._pkgindex_file = self._bintree._pkgindex_file
		self._pkgindex = self._bintree._load_pkgindex()

	def check(self, onProgress=None):
		missing = []
		cpv_all = self._bintree.dbapi.cpv_all()
		cpv_all.sort()
		maxval = len(cpv_all)
		if onProgress:
			onProgress(maxval, 0)
		pkgindex = self._pkgindex
		missing = []
		metadata = {}
		for d in pkgindex.packages:
			metadata[d["CPV"]] = d
		for i, cpv in enumerate(cpv_all):
			d = metadata.get(cpv)
			if not d or "MD5" not in d:
				missing.append(cpv)
			if onProgress:
				onProgress(maxval, i+1)
		errors = ["'%s' is not in Packages" % cpv for cpv in missing]
		stale = set(metadata).difference(cpv_all)
		for cpv in stale:
			errors.append("'%s' is not in the repository" % cpv)
		return errors

	def fix(self, onProgress=None):
		bintree = self._bintree
		cpv_all = self._bintree.dbapi.cpv_all()
		cpv_all.sort()
		missing = []
		maxval = 0
		if onProgress:
			onProgress(maxval, 0)
		pkgindex = self._pkgindex
		missing = []
		metadata = {}
		for d in pkgindex.packages:
			metadata[d["CPV"]] = d

		for i, cpv in enumerate(cpv_all):
			d = metadata.get(cpv)
			if not d or "MD5" not in d:
				missing.append(cpv)

		stale = set(metadata).difference(cpv_all)
		if missing or stale:
			from portage import locks
			pkgindex_lock = locks.lockfile(
				self._pkgindex_file, wantnewlockfile=1)
			try:
				# Repopulate with lock held.
				bintree._populate()
				cpv_all = self._bintree.dbapi.cpv_all()
				cpv_all.sort()

				pkgindex = bintree._load_pkgindex()
				self._pkgindex = pkgindex

				metadata = {}
				for d in pkgindex.packages:
					metadata[d["CPV"]] = d

				# Recount missing packages, with lock held.
				del missing[:]
				for i, cpv in enumerate(cpv_all):
					d = metadata.get(cpv)
					if not d or "MD5" not in d:
						missing.append(cpv)

				maxval = len(missing)
				for i, cpv in enumerate(missing):
					try:
						metadata[cpv] = bintree._pkgindex_entry(cpv)
					except portage.exception.InvalidDependString:
						writemsg("!!! Invalid binary package: '%s'\n" % \
							bintree.getname(cpv), noiselevel=-1)

					if onProgress:
						onProgress(maxval, i+1)

				for cpv in set(metadata).difference(
					self._bintree.dbapi.cpv_all()):
					del metadata[cpv]

				# We've updated the pkgindex, so set it to
				# repopulate when necessary.
				bintree.populated = False

				del pkgindex.packages[:]
				pkgindex.packages.extend(metadata.values())
				from portage.util import atomic_ofstream
				f = atomic_ofstream(self._pkgindex_file)
				try:
					self._pkgindex.write(f)
				finally:
					f.close()
			finally:
				locks.unlockfile(pkgindex_lock)

		if onProgress:
			if maxval == 0:
				maxval = 1
			onProgress(maxval, maxval)
		return None
