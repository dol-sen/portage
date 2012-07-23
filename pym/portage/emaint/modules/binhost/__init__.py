#!/usr/bin/python -O
#
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'The emaint program module provides checks and maintenancefor:
  Scanning, checking and fixing problems in the world file.
"""


module_spec = {
	'name': 'binhost',
	'description': "Provides functions to scan, check and " + \
		"Generate a metadata index for binary packages",
	'provides':{
		'module1': {
			'name': "binhost",
			'class': "BinhostHandler",
			'description':  "Generate a metadata index for binary packages",
			'functions': ['check', 'fix'],
			'func_desc': {}
			}
		}
	}
