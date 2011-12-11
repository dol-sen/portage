#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'This emaint module provides checks and maintenance for:
Cleaning the emerge config tracker list
"""


module_spec = {
	'name': 'config',
	'description': "Provides functions to scan, check for and fix no " +\
		"longer installed config files in emerge's tracker file",
	'provides':{
		'module1': {
			'name': "cleanconfig",
			'class': "CleanConfig",
			'description':  "Discard no longer installed config tracker entries",
			'functions': ['check', 'fix'],
			'func_desc': {}
			}
		}
	}
