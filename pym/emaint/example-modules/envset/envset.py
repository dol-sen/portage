#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'This emaint program module provides  a test of environment set
changes which change the class exported via the plug-in system.
"""

from __future__ import print_function


class EnvOne(object):

	short_desc = "Print out the Class bieng run"

	def name():
		return "evnset - EnvOne"
	name = staticmethod(name)


	def check(self, onProgress=None):
		print("\n You've reached the EnvOne class check()")


	def fix(self, onProgress=None):
		print("\n You've reached the EnvOne class fix()")


class EnvTwo(object):

	short_desc = "Print out the Class bieng run"

	def name():
		return "evnset - EnvTwo"
	name = staticmethod(name)


	def check(self, onProgress=None):
		print("\n You've reached the EnvTwo class check()")


	def fix(self, onProgress=None):
		print("\n You've reached the EnvTwo class fix()")


class EnvThree(object):

	short_desc = "Print out the Class bieng run"

	def name():
		return "evnset - EnvThree"
	name = staticmethod(name)


	def check(self, onProgress=None):
		print("\n You've reached the EnvThree class check()")


	def fix(self, onProgress=None):
		print("\n You've reached the EnvThree class fix()")

