#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'This emaint module provides checks and maintenance for:
Cleaning the "emerge --resume" lists
"""


module_spec = {
	'name': 'resume',
	'description': "Provides functions to scan, check and fix problems " +\
		"in the resume and/or resume_backup files",
	'provides':{
		'module1': {
			'name': "cleanresume",
			'class': "CleanResume",
			'description':  "Discard emerge --resume merge lists",
			'options': ['check', 'fix']
			}
		}
	}
