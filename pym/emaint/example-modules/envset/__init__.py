#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'This emaint program module provides checks for a test of 
environment set changes which change the class exported via the plug-in system.
"""

import os

DEFAULT_CLASS = "EnvOne"
AVAILABLE_CLASSES = [ "EnvOne",  "EnvTwo",  "EnvThree"]
options = {"1": "EnvOne", "2": "EnvTwo", "3": "EnvThree"}


config_class = DEFAULT_CLASS
try:
	test_param = os.environ["TESTIT"]
	if test_param in options:
		config_class = options[test_param]
except KeyError:
	pass


module_spec = {
	'name': 'testdummy',
	'description': "Provides functions to scan, check and " + \
		"Generate an example auto config module",
	'provides':{
		'module1': {
			'name': "envset",
			'class': config_class,
			'description':  "Dummy module used to test environment settings " + \
					"to change the class being exported by the plug-in system",
			'functions': ['check', 'fix'],
			'func_desc': {}
			}
		}
	}
