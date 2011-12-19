#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'This example emaint module provides checks and maintenance for:
Cleaning the "emerge --resume" lists.  It extends it to show the use of
options other than the default check,fix.
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
			'functions': ['check', 'fix'],
			'func_desc': {}
			},
		'module2': {
			'name': "setresume",
			'class': "SetResume",
			'description':  "list, Save, Restore emerge --resume merge lists",
			'functions': ['list', 'save', 'restore'],
			'func_desc': {
				'list': {
					"short": "-l", "long": "--list",
					"help": "[setresume] Lists the resume list",
					'status': "Listing %s",
					'func': 'list'
					},
				
				'save':{
					"short": "-s", "long": "--save",
					"help": '[setresume] Saves the resume list',
					'status': "Saving list to: %s",
					'func': 'save'
					},

				'restore':{
					"short": "-r", "long": "--restore",
					"help": '[setresume] Restores a resume list from a saved list',
					'status': "Restoring %s list",
					'func': 'restore'
					},
				
				}
			}

		}
	}
