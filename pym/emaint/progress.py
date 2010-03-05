#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$


from __future__ import print_function


import time
import signal

import portage


class ProgressHandler(object):
	def __init__(self):
		self.reset()

	def reset(self):
		self.curval = 0
		self.maxval = 0
		self.last_update = 0
		self.min_display_latency = 0.2

	def onProgress(self, maxval, curval):
		self.maxval = maxval
		self.curval = curval
		cur_time = time.time()
		if cur_time - self.last_update >= self.min_display_latency:
			self.last_update = cur_time
			self.display()

	def display(self):
		raise NotImplementedError(self)


