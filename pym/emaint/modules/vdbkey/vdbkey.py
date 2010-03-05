#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function

import re

import portage
from portage import os


class VdbKeyHandler(object):

	short_desc = "Perform checks and fixes problems with an " + \
		"installed package's data"

	def name():
		return "vdbkeys"
	name = staticmethod(name)

	def __init__(self):
		self.list = portage.db["/"]["vartree"].dbapi.cpv_all()
		self.missing = []
		self.keys = ["HOMEPAGE", "SRC_URI", "KEYWORDS", "DESCRIPTION"]

		for p in self.list:
			mydir = os.path.join(os.sep, portage.settings["ROOT"], portage.const.VDB_PATH, p)+os.sep
			ismissing = True
			for k in self.keys:
				if os.path.exists(mydir+k):
					ismissing = False
					break
			if ismissing:
				self.missing.append(p)

	def check(self, onProgress=None):
		"""@param onProgress: default is None,
		is not used, is only there for module compatibility."""
		return ["%s has missing keys" % x for x in self.missing]

	def fix(self, onProgress=None):

		errors = []

		maxval = len(self.missing)
		if onProgress:
			onProgress(maxval, 0)
		for p in self.missing:
			mydir = os.path.join(os.sep, portage.settings["ROOT"], portage.const.VDB_PATH, p)+os.sep
			if not os.access(mydir+"environment.bz2", os.R_OK):
				errors.append("Can't access %s" % (mydir+"environment.bz2"))
			elif not os.access(mydir, os.W_OK):
				errors.append("Can't create files in %s" % mydir)
			else:
				env = os.popen("bzip2 -dcq "+mydir+"environment.bz2", "r")
				envlines = env.read().split("\n")
				env.close()
				for k in self.keys:
					s = [l for l in envlines if l.startswith(k+"=")]
					if len(s) > 1:
						errors.append("multiple matches for %s found in %senvironment.bz2" % (k, mydir))
					elif len(s) == 0:
						s = ""
					else:
						s = s[0].split("=",1)[1]
						s = s.lstrip("$").strip("\'\"")
						s = re.sub("(\\\\[nrt])+", " ", s)
						s = " ".join(s.split()).strip()
						if s != "":
							try:
								keyfile = open(mydir+os.sep+k, "w")
								keyfile.write(s+"\n")
								keyfile.close()
							except (IOError, OSError) as e:
								errors.append("Could not write %s, reason was: %s" % (mydir+k, e))
			if onProgress:
				onProgress(maxval, i+1)

		return errors
